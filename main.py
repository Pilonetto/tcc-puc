# -*- coding: utf-8 -*-
"""
Created on Sun Jul 26 08:21:38 2020

@author: Marlon
"""

# Biblitecas para Web Scraping
import bs4
import json
import requests
from bs4 import BeautifulSoup as bs

# Biblitecas para visualização e análise de dados
import re
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.cluster import KMeans



# Função que salva o conteúdo de cada página (as receitas de cada página) em um arquivo JSON
def salva_receita(title, 
                  layout, 
                  picture, 
                  servings, 
                  ingredients, 
                  method, 
                  prep_time, 
                  cook_time, 
                  additional_time, 
                  total_time):
    
    # Cria uma lista para receber o conteúdo das páginas, ou seja, todas as receitas em cada página
    lista_receitas = []
        
    # Define o nome do arquivo em disco
    receitas_arquivo = Path("C:/Python/TCC/dados/dataset.json")
    
    # Verifica se o arquivo existe em disco e se existir carregamos o arquivo
    if receitas_arquivo.is_file():
        with open(receitas_arquivo) as in_file:
            lista_receitas = json.load(in_file)
        
        # Atribui False à variável de controle
        ja_existe = False
        
        # Vamos checar se a receita já está na lista
        for receita in lista_receitas:
            if receita['titulo'] == title:
                ja_existe = True
        
        # Se a receita não estiver na lista, então incluímos a receita
        if not ja_existe:
            print("Receita Incluída na Lista: {} ".format(title))
            nova_receita = {}
            nova_receita['titulo'] = title
            nova_receita['layout'] = layout
            nova_receita['imagem'] = picture
            nova_receita['ingredientes'] = ingredients
            nova_receita['metodo'] = method
            nova_receita['porcoes'] = servings
            nova_receita['tempo_preparo'] = prep_time
            nova_receita['tempo_cozimento'] = cook_time
            nova_receita['tempo_adicional'] = additional_time
            nova_receita['tempo_total'] = total_time
        
            # Adiciona a nova receita na lista
            lista_receitas.append(nova_receita)
    
            # Grava no arquivo
            with open('C:/Python/TCC/dados/dataset.json', 'w') as arquivo:
                json.dump(lista_receitas, arquivo, indent = 4)
        else:
            print("Esta Receita já está na Lista: {} ".format(title))
            
    # Se o arquivo não existir, será criado pela primeira vez já com as receitas da primeira página 
    else:
        print("Título da Receita: {} ".format(title))
        nova_receita = {}
        nova_receita['titulo'] = title
        nova_receita['layout'] = layout
        nova_receita['imagem'] = picture
        nova_receita['ingredientes'] = ingredients
        nova_receita['metodo'] = method
        nova_receita['porcoes'] = servings
        nova_receita['tempo_preparo'] = prep_time
        nova_receita['tempo_cozimento'] = cook_time
        nova_receita['tempo_adicional'] = additional_time
        nova_receita['tempo_total'] = total_time
        
        # Adiciona a nova receita na lista
        lista_receitas.append(nova_receita)
    
        # Grava no arquivo
        with open('C:/Python/TCC/dados/dataset.json', 'w') as arquivo:
            json.dump(lista_receitas, arquivo, indent = 4)
            
# Vamos definir quantas páginas de dados serão extraídas
# Evite colocar muitas páginas, pois o processo pode ser demorado
primeira_pagina = 1
ultima_pagina = 10


print("Iniciando Web Scraping! Isso vai demorar. Seja paciente!")

# Loop pelo range de páginas que você definiu com os 2 parâmetros anteriores
for page in range(primeira_pagina, ultima_pagina + 1):
    
    # Requisição à página
    source = requests.get("https://www.allrecipes.com/recipes?page=" + str(page))
    print("\nPágina Sendo Processada: {}".format(page))
    
    # Código fonte (HTML) da página
    doc = bs(source.text, 'html.parser')
    
    # Selecionamos cada receita vinculada à página e abrimos os links um por um
    recipe_cards = doc.select('a.fixed-recipe-card__title-link')

    # Loop por todas as receitas de cada página
    for card in recipe_cards:
        
        # Aqui estão os dados que iremos extrair
        # Vamos criar e inicializar as variáveis
        layout = 0
        ingredients_list = []
        method_list = []
        title, picture = '', ''
        prep_time, cook_time, total_time, additional_time, servings, = '','','','',''
        
        # Abrimos então a página de cada receita e fazemos o parse do código HTML
        recipe_page_source = requests.get(card['href'])    
        
        # Copiamos então o conteúdo principal da página (texto da receita)
        recipe_main = bs(recipe_page_source.text, 'html.parser')
        
        # Agora pesquisamos pelos dados que declaramos acima
        title = recipe_main.select_one('.recipe-summary__h1')
        
        # Se o título não estiver em branco, extraímos os dados e nesse caso o layout é 1
        if title is not None:
            layout = 1
            title = title.text
            picture = recipe_main.select_one('.rec-photo').attrs['src']
            ingredients = recipe_main.select('.recipe-ingred_txt')
            method = recipe_main.select('.recipe-directions__list--item')
            servings = recipe_main.select_one('#metaRecipeServings')['content']
            meta_item_types = recipe_main.select('.prepTime__item--type')
            meta_item_times = recipe_main.select('.prepTime__item--time')
            
            # Queremos os tempos de preparo de cada receita. Vamos extrair.
            for label, time in zip(meta_item_types, meta_item_times):
                if label.text == 'Prep':
                    prep_time = time.text
                elif label.text =='Cook':
                    cook_time = time.text
                elif label.text == 'Additional':
                    additional_time = time.text
                elif label.text == 'Ready In':
                    total_time = time.text                
                
        # Se o título for None, a página é diferente e nesse caso o layout é igual a 2
        else:
            layout = 2
            title = recipe_main.select_one('h1.headline.heading-content').text
            picture = recipe_main.select_one('.inner-container > img').attrs['src']
            ingredients = recipe_main.select('span.ingredients-item-name')
            method = recipe_main.select('div.paragraph > p')
            meta_items = recipe_main.select('div.recipe-meta-item')
            
            for item in meta_items:
                parts = item.select('div')
                header = parts[0].text.strip()
                body = parts[1].text.strip()
                    
                if header == 'prep:':
                    prep_time = body
                elif header =='cook:':
                    cook_time = body
                elif header == 'additional:':
                    additional_time = body
                elif header == 'total:':
                    total_time = body
                elif header == 'Servings:':
                    servings = body
        
        # Compilamos a lista de ingredientes da receita
        for ingredient in ingredients:
            if ingredient.text != 'Add all ingredients to list' and ingredient.text != '':
                ingredients_list.append(ingredient.text.strip())
            
        # Compilamos a lista de métodos da receita
        for instruction in method:
            method_list.append(instruction.text.strip())
        
        # Se ingredientes ou lista de métodos estiverem vazios, não gravamos os dados
        if len(ingredients_list)==0 and len(method_list) == 0:
            pass
        else:
            # Se tudo ok chamamos a função e gravamos os dados em disco
            salva_receita(title, layout, picture, servings, ingredients_list, method_list, 
                          prep_time, cook_time, additional_time, total_time)
        
print("Web Scraping Concluído com Sucesso!")

# Começamos carregando o arquivo
dados = pd.read_json(r'C:/Python/TCC/dados/dataset.json')

# Vamos organizar as colunas
dados = dados[['titulo', 
               'porcoes', 
               'tempo_cozimento', 
               'tempo_preparo', 
               'tempo_adicional', 
               'tempo_total', 
               'ingredientes', 
               'metodo', 
               'layout', 
               'imagem']]


# Lista de palavras que representam medidas de unidade. Não pecisaremos disso.
medidas_unidades = ['gallon',
                    'quart',
                    'pint',
                    'cup',
                    'teaspoon',
                    'tablespoon',
                    'ounce',
                    'pound',
                    'can',
                    'pinch',
                    'serving',
                    'slice',
                    'package',
                    'bottle']

# Lista de descritores. Isso também não será necessário.
descritores = ['small', 'medium', 'large']

# Lista para os ingredientes depois da limpeza
lista_ingredientes_limpos = []

# Loop pela coluna de ingredientes de cada receita
for item in dados['ingredientes']:
    
    # Ingrediente a ser processado
    lista_ings = item
    
    # Remove medidas de unidade e descritores
    for palavra in medidas_unidades + descritores:
        plural = palavra + "s"
        lista_ings = [item.replace(' ' + plural + ' ', ' ') for item in lista_ings]
        lista_ings = [item.replace(' ' + palavra + ' ',' ') for item in lista_ings]    
    
    # Remove outros descritores comuns
    lista_ings = [item.replace('boneless,','') for item in lista_ings] 
    lista_ings = [item.replace('skinless,','') for item in lista_ings] 
    lista_ings = [item.replace('boneless','') for item in lista_ings] 
    lista_ings = [item.replace('skinless','') for item in lista_ings] 
    
    # Remove parenteses
    lista_ings = [re.sub(r'\([^()]*\)','', item) for item in lista_ings]
    
    # Divide texto depois de vírgulas
    lista_ings = [item.partition(',')[0] for item in lista_ings] 
    
    # Remove qualquer coisa que não seja caracter
    lista_ings = [re.sub(r'[^a-zA-Z]', ' ', item) for item in lista_ings]
    
    # Removemos espaços adicionais que ficaram depois de remover os itens anteriores
    lista_ings = [item.strip() for item in lista_ings] 

    # Substituímos o plural pelo singular
    lista_ings = [item.replace('eggs', 'egg') for item in lista_ings] 
    
    # Passamos os dados para um objeto temporário
    temp = lista_ings
    
    # Limpamos a lista
    lista_ings = []
    
    # Checamos pelos últimos elementos
    for item in temp:
        if 'chicken breast' in item:
            ing = 'chicken breast'
        elif 'chicken thigh' in item:
            ing = 'chicken thigh'
        elif 'chicken stock' in item:
            ing = 'chicken stock'
        elif 'ground beef' in item:
            ing = 'ground beef'
            
        # Adicionamos o item à lista    
        lista_ings.append(item)
    
    lista_ingredientes_limpos.append(lista_ings)

# Criamos uma nova coluna no dataset após a limpeza
dados['ingredientes_limpos'] = lista_ingredientes_limpos 

# Visualizamos os dados antes e depois da limpeza
dados_limpos = dados[['ingredientes', 'ingredientes_limpos']]     


# Lista de ingredientes
lista_ingredientes = []

# Loop
for linha in dados['ingredientes_limpos']:
    for item in linha:
        lista_ingredientes.append(str(item).lower())
        
for i in range(len(lista_ingredientes)):
    lista_ingredientes[i] = lista_ingredientes[i].lower()        

# Dataframe de ingredientes
ingredientes = pd.DataFrame(lista_ingredientes, columns = ['ingrediente'])      

# Plot dos ingredientes mais comuns
n = 20
fig, ax = plt.subplots(figsize = (12, 12))
bar_positions = np.arange(n)
bar_heights = ingredientes['ingrediente'].value_counts().head(n)
bar_names = ingredientes['ingrediente'].value_counts().head(n).index
ax.barh(bar_positions, bar_heights, 0.6, color = 'green')
ax.set_yticks(bar_positions)
ax.set_yticklabels(bar_names)
ax.set_title('30 Ingredientes Mais Comuns (em ' + str(dados.shape[0]) + ' Receitas)')
ax.set_ylabel('\nIngredientes')
ax.set_xlabel('\nFrequência')
ax.invert_yaxis()
plt.show() 


# Define um determinado ingrediente
ingrediente_escolhido = 'butter'

# Lista de valores booleanos
lista_verifica_ingrediente = []

# Lista para os pares dos ingredientes
pares_ingredientes = []

# Loop que verifica se o ingrediente que escolhemos ("butter") existe na lista de ingredientes limpos
for linha in dados['ingredientes_limpos']:
    
    tem_ing = False
    
    for item in linha:
        if item == ingrediente_escolhido:
            tem_ing = True
            
    lista_verifica_ingrediente.append(tem_ing)
    
# Loop para buscar os ingredientes que aparecem sempre que "potatoes" aparece na receita
for linha in dados[lista_verifica_ingrediente]['ingredientes_limpos']:
    
    for item in linha:
        if item == ingrediente_escolhido:
            continue
        else:
            pares_ingredientes.append(item)


# Cria o dataframe
df_pares_ingredientes = pd.DataFrame(pares_ingredientes, columns = ['pares'])

# Plot
n = 20
fig, ax = plt.subplots(figsize = (5,5))
bar_positions = np.arange(n)
bar_heights = df_pares_ingredientes['pares'].value_counts().head(n)
bar_names = df_pares_ingredientes['pares'].value_counts().head(n).index
ax.barh(bar_positions, bar_heights, 0.5, color = 'cyan')
ax.set_yticks(bar_positions)
ax.set_yticklabels(bar_names)
ax.set_title('\nIngredientes Mais Comuns com ' + ingrediente_escolhido.lower().capitalize() 
             + ' (' + str(dados.shape[0]) + ' Receitas)\n')
ax.set_ylabel('\nIngredientes')
ax.set_xlabel('\nFrequência')
ax.invert_yaxis()
plt.show()            


# Salvar os 200 ingredientes mais usados
ingredientes['ingrediente'].value_counts().head(200).to_csv('dados/ingredientes.csv',header=True, sep=';')

#Nes te instervalo foi feita a classificação manual dos ingredientes

ingredientes_classificados = pd.read_csv('C:/Python/TCC/dados/ingredientes.csv', sep=',') 



valores = ingredientes['ingrediente'].value_counts()
ingredientes_unicos = ingredientes.drop_duplicates()

dados['potencial_risco'] = 0

def order_cluster(cluster_field_name, target_field_name,df,ascending):
    df_new = df.groupby(cluster_field_name)[target_field_name].mean().reset_index()
    df_new = df_new.sort_values(by=target_field_name,ascending=ascending).reset_index(drop=True)
    df_new['index'] = df_new.index
    df_final = pd.merge(df,df_new[[cluster_field_name,'index']], on=cluster_field_name)
    df_final = df_final.drop([cluster_field_name],axis=1)
    df_final = df_final.rename(columns={"index":cluster_field_name})
    return df_final

def risco_ingrediente(ingrediente):
    x = 0
    for row in ingredientes_classificados.iterrows():
        if (ingrediente.lower().find(row[1][0].lower())) >= 0:
            x += row[1][1]    
    print('Risco: ' + str(ingrediente) + ' ' + str(x))    
    return x

for row in dados.iterrows():
    x = 0

    for ingrediente in row[1][10]:
        try:
            x+= risco_ingrediente(str(ingrediente))
        except KeyboardInterrupt:
            break            
        except:continue
    dados.at[row[0],'potencial_risco'] = x
    
dados_amostra = dados[['titulo','ingredientes','potencial_risco']]
#dados['somatorio'] = 0

#for row in dados.iterrows():
#    x = 0

#    for ingrediente in row[1][10]:
#        try:
#            x+= valores[valores.index == ingrediente][0]
#        except KeyboardInterrupt:
#            break            
#        except:continue
#    print(row[0],x)
#    dados.at[row[0],'somatorio'] = x
    
## Aprendizado de maquina
    
kmeans = KMeans(n_clusters=3)
kmeans.fit(dados[['potencial_risco']])
dados['risco_cluster'] = kmeans.predict(dados[['potencial_risco']])    

dados = order_cluster('risco_cluster', 'potencial_risco',dados,True)
dados['classificacao_texto'] = 'Risco muito baixo'
dados.loc[dados['risco_cluster'] == 1, 'classificacao_texto'] = 'Risco moderado'
dados.loc[dados['risco_cluster'] == 2, 'classificacao_texto'] = 'Risco alto'

# Plot
fig, ax = plt.subplots(figsize = (5,5))
bar_positions = np.arange(n)
bar_heights = dados['risco_cluster'].value_counts()
bar_names = dados['classificacao_texto'].value_counts().index

ax.barh(bar_positions, bar_heights, 0.5, color = 'cyan')
ax.set_yticks(bar_positions)
ax.set_yticklabels(bar_names)

ax.set_ylabel('\nIngredientes')
ax.set_xlabel('\nFrequência')
ax.invert_yaxis()
plt.show()   
