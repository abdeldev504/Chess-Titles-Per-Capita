import pandas as pd
import requests
from bs4 import BeautifulSoup
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Fonction pour récupérer et préparer les données FIDE
def get_fide_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find_all('table')[4]
    
    # Conversion de la table HTML en DataFrame
    fide_df = pd.read_html(str(table))[0]
    
    # Nettoyage et préparation du DataFrame
    fide_df.columns = fide_df.iloc[1]
    fide_df = fide_df[2:].dropna(axis=1, how='all')
    fide_df.columns = fide_df.columns.str.strip()
    fide_df.columns = ['Rank', 'Federation', 'Average', 'GMs', 'IMs', 'Total Titled']
    
    # Conversion des colonnes pertinentes en numériques
    fide_df[['GMs', 'IMs', 'Total Titled']] = fide_df[['GMs', 'IMs', 'Total Titled']].apply(pd.to_numeric, errors='coerce')
    
    return fide_df

# Fonction pour récupérer les données de population depuis Wikipedia
def get_population_data(url):
    pop_tables = pd.read_html(url)
    pop_df = pop_tables[0]
    pop_df.columns = ['_'.join(col).strip() for col in pop_df.columns.values]
    pop_df = pop_df[['L_o_c_a_t_i_o_n', 'P_o_p_u_l_a_t_i_o_n']]
    pop_df.columns = ['Country', 'Population']
    
    return pop_df

# Fonction pour agréger les données du Royaume-Uni
def aggregate_uk_data(fide_df, uk_countries):
    uk_data = fide_df[fide_df['Federation'].isin(uk_countries)]
    uk_aggregated = uk_data[['GMs', 'IMs', 'Total Titled']].sum()
    uk_aggregated['Federation'] = 'United Kingdom'
    return pd.DataFrame([uk_aggregated])

# Fonction pour corriger les noms des pays
def correct_country_names(df, corrections):
    df['Country'] = df['Country'].replace(corrections)
    return df

# Fonction pour fusionner les données FIDE et population
def merge_fide_population_data(fide_df, pop_df):
    return pd.merge(fide_df, pop_df, left_on='Federation', right_on='Country', how='inner')

# Fonction pour calculer les titres par million d'habitants
def calculate_titled_per_million(merged_df):
    merged_df['Total titled per million'] = merged_df['Total Titled'] / (merged_df['Population'] / 1_000_000)
    return merged_df

# Fonction pour créer un GeoDataFrame pour les pays manquants
def create_missing_countries_geometries():
    missing_countries = {
        'Monaco': Point(7.4246, 43.7384),
        'San Marino': Point(12.4578, 43.9424),
        'Liechtenstein': Point(9.5554, 47.1660),
        'Andorra': Point(1.5218, 42.5063),
        'Malta': Point(14.3754, 35.9375),
        'Bosnia & Herzegovina': Point(17.6791, 43.9159),
        'Seychelles': Point(55.4919, -4.6796),
        'Trinidad & Tobago': Point(-61.2225, 10.6918),
        'Singapore': Point(103.8198, 1.3521),
        'Maldives': Point(73.2207, 3.2028),
        'Bahrain': Point(50.5577, 26.0667),
        'Hong Kong, China': Point(114.1694, 22.3193),
        'Eswatini': Point(31.4659, -26.5225),
        'Antigua and Barbuda': Point(-61.7964, 17.0608),
        'Cape Verde': Point(-23.6042, 15.1201),
    }
    return gpd.GeoDataFrame({
        'name': list(missing_countries.keys()),
        'geometry': list(missing_countries.values())
    }, crs="EPSG:4326")

# Fonction pour tracer la carte
def plot_map(world, new_countries, colors):
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    world.boundary.plot(ax=ax, linewidth=0.1)
    world.plot(ax=ax, color=world['color'], edgecolor='black')
    
    # Enlever les axes
    ax.axis('off')
    
    # Ajouter une légende
    legend_labels = {
        '#001A00': '30+',
        '#003C00': '15-30',
        '#007F00': '5-15',
        '#D3FF00': '2-5',
        '#FFD215': '1-2',
        '#FF852F': '0.25-1',
        '#FF5B00': '0-0.25',
        '#C0C0C0': 'Groenland'
    }
    patches = [mpatches.Patch(color=color, label=label) for color, label in legend_labels.items()]
    plt.legend(handles=patches, loc='lower left', title="Titres par million d'habitants")
    
    plt.title("Densité des titres d'échecs par pays selon la FIDE")
    plt.show()


# Programme principal
fide_url = "https://ratings.fide.com/topfed.phtml?tops=0&ina=2&country="
wiki_pop_url = "https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_population"

fide_df = get_fide_data(fide_url)
pop_df = get_population_data(wiki_pop_url)

uk_countries = ['England', 'Scotland', 'Wales', 'Northern Ireland']
uk_aggregated_df = aggregate_uk_data(fide_df, uk_countries)
fide_df = pd.concat([fide_df, uk_aggregated_df], ignore_index=True)

corrections = {
    'United States': 'United States of America',
    'Dominican Republic': 'Dominican Rep.',
    'Hong Kong (China)': 'Hong Kong, China',
    'Trinidad and Tobago': 'Trinidad & Tobago',
    'Guernsey (UK)': 'Guernsey',
    'Aruba (Netherlands)': 'Aruba',
    'Brunei': 'Brunei Darussalam',
    'Guam (US)': 'Guam',
    'Chinese Taipei': 'Taiwan',
    'East Timor': 'Timor-Leste',
    'Puerto Rico (US)': 'Puerto Rico',
    'Bosnia and Herzegovina': 'Bosnia & Herzegovina',
    'Jersey (UK)': 'Jersey',
    'Bermuda (UK)': 'Bermuda',
    'U.S. Virgin Islands (US)': 'US Virgin Islands',
    'Faroe Islands (Denmark)': 'Faroe Islands',
    'Macau (China)': 'Macau',
    'Democratic Republic of the Congo': 'Dem. Rep. Congo',
    'South Sudan': 'S. Sudan',
    "Ivory Coast": "Côte d'Ivoire",
    "Czech Republic": "Czechia"
}
pop_df = correct_country_names(pop_df, corrections)
fide_df['Federation'] = fide_df['Federation'].replace(corrections)

merged_df = merge_fide_population_data(fide_df, pop_df)
merged_df = calculate_titled_per_million(merged_df)

# Définir les catégories et les couleurs
bins = [0, 0.25, 1, 2, 5, 15, 30, float('inf')]
labels = ['0-0.25', '0.25-1', '1-2', '2-5', '5-15', '15-30', '30+']
merged_df['category'] = pd.cut(merged_df['Total titled per million'], bins=bins, labels=labels, include_lowest=True)
colors = {
    '30+': '#001A00', 
    '15-30': '#003C00',
    '5-15': '#007F00',
    '2-5': '#D3FF00',
    '1-2': '#FFD215',
    '0.25-1': '#FF852F',
    '0-0.25': '#FF5B00'
}

# Charger la carte du monde et ajouter les pays manquants
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
new_countries = create_missing_countries_geometries()
world = pd.concat([world, new_countries], ignore_index=True)

# Fusionner la géométrie du Somaliland avec la Somalie
if 'Somalia' in world['name'].values and 'Somaliland' in world['name'].values:
    somalia_geom = world.loc[world['name'] == 'Somalia', 'geometry'].values[0]
    somaliland_geom = world.loc[world['name'] == 'Somaliland', 'geometry'].values[0]
    world.loc[world['name'] == 'Somalia', 'geometry'] = somalia_geom.union(somaliland_geom)
    world = world[world['name'] != 'Somaliland']

# Fusionner la géométrie du Sahara Occidental avec le Maroc 
if 'Morocco' in world['name'].values and 'W. Sahara' in world['name'].values:
    morocco_geom = world.loc[world['name'] == 'Morocco', 'geometry'].values[0]
    western_sahara_geom = world.loc[world['name'] == 'W. Sahara', 'geometry'].values[0]
    world.loc[world['name'] == 'Morocco', 'geometry'] = morocco_geom.union(western_sahara_geom)
    world = world[world['name'] != 'W. Sahara']

# Supprimer l'Antarctica du DataFrame 'world'
world = world[world['name'] != 'Antarctica']

# Fusionner les données géographiques avec les données FIDE
world = world.merge(merged_df, how="left", left_on="name", right_on="Country")

# Appliquer les couleurs
world['color'] = world.apply(
    lambda row: '#C0C0C0' if row['name'] == 'Greenland' else colors.get(row['category'], '#FF5B00'),
    axis=1
)

# Tracer la carte
plot_map(world, new_countries, colors)


