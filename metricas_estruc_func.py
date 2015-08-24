# -*- coding: utf-8 -*-
"""
Created on Sun Aug 23 18:08:18 2015

@author: john
"""
import arcpy
from arcpy import env
import os
import sys
import arcpy.mapping
arcpy.env.overwriteOutput = True
arcpy.env.parallelProcessingFactor = "80%"



path_work=r"E:\_data\__GabiBeca_Analises_Finais\Mestrado_Gabrielle_Paisagem\Clips_Mestrado"
arcpy.env.workspace=path_work

def insert(frags_com_pacth):
    #data frame atual
    mxd = arcpy.mapping.MapDocument("CURRENT")

    # get the data frame    
    df = arcpy.mapping.ListDataFrames(mxd,"*")[0]

    # create a new layer
    newlayer = arcpy.mapping.Layer(frags_com_pacth)

    # add the layer to the map at the bottom of the TOC in data frame 0
    arcpy.mapping.AddLayer(df, newlayer,"BOTTOM")




def criar_buffer_mapa_veg(mapa,path_work):
    """
    Essa funcao vai gerar um bauffer de 100 em funcao de todos os fragmentos de vegetacao
    
    paramentros da funcao
    mapa=mapa de vegetacao
    path_work=pastas onde estao sendo salvos os arquivos
    """    
    
    #criando buffer
    arcpy.Buffer_analysis(mapa, mapa+'_100m', "100 Meters", "FULL", "ROUND", "ALL", "")
    # fazendo explod para evitar que selecione poligonos errados
    arcpy.MultipartToSinglepart_management(path_work+"/"+mapa+'_100m.shp',path_work+"/"+mapa+'_100m_explod')
    # inserindo no o mapa resultante no projeto
    insert(path_work+"/"+mapa+'_100m_explod.shp')
#executando a funcao    
criar_buffer_mapa_veg("clip_buffer10000m_mestrado_gabrielle",path_work)


        
        
   
    
# buffer vazio
class MethodsArcpy(object):
    def __init__(self):
        print "Metodo constrututor das fucoes arcpy chamado com sucesso"
        """
        Vars
        self.mapa_veg=variavel que recebe o mapa de vegetacao, essa variavel vai ser preenchida na classe principal
        self.query=expressao para selecao, vai ser preenchida na classe principal
        self.mapa_pnt=mapa de buffer de 2k, servira para fazer um select by location no mapa de 10k

        """        
        
        self.mapa_veg=''
        self.query=''
        self.mapa_buff=''
        
    def selecByAtributes(self):
        """
        Seleciona por uma expressao de atributo
        parametros: mapa_buff, query
        """         
        arcpy.SelectLayerByAttribute_management(self.mapa_buff,"NEW_SELECTION",self.query)
        
    def Clear_selection(self):
        """
        Limpa selecao 
        parametros: mapa
        """        
        arcpy.SelectLayerByAttribute_management(self.mapa_buff,"CLEAR_SELECTION")

    def selectByLocation(self):
        """
        Seleciona um conjunto de poligono atraves de um outro shp
        Parametros:
        1-mapa a ser selecionado
        2-metodo
        3-mapa que sera usado como base
        """
        arcpy.SelectLayerByLocation_management(self.mapa_veg,"INTERSECT",self.mapa_buff)
        
    def sum_selection(self):
        """
        Faz a soma  da coluna area selecionada e retorna o resultado
        parametros:
        Mapa,coluna          
        """
        field = arcpy.da.TableToNumPyArray (self.mapa_veg, "area_HA", skip_nulls=True)
        sum = field["area_HA"].sum() 
        return sum

class metrica_pai_GAP(MethodsArcpy):
    #passei uma classe por parametro, isso é uma heraca(MethodsArcpy)

    def __init__(self,mapa_veg,mapa_buff):
        MethodsArcpy.__init__(self)
        """
        Vars:
        self.mapa_pnt=mapa_buff ------> esta preenchendo uma variavel da classe MethodsArcpy com o mapa de buffer de 2k 
        self.mapa_veg=mapa_veg  ------> esta preenchendo uma variavel da classe MethodsArcpy com o mapa vegetacao clipado de 10k
        self.result_sum='' Variavel da classe metreica_paiGAp, recebe o resultado da soma   
        """
        self.mapa_pnt=mapa_buff
        self.mapa_veg=mapa_veg
        self.result_sum=''        
        
    def travels_buffer(self):
        #mudando o caminho onde sera salvo o tt
        os.chdir(path_work)
        #abrindo o txt
        self.txt=open('Estructure_functional.txt','w')
        #lendo o cabeçalho
        self.txt.write("Pai"+"	"+"Area_Sum\n")
        
        #Abrindo o self.mapa_buff capturando a coluna FID
        with arcpy.da.SearchCursor(self.mapa_buff,"FID") as cursor:
            # for nas linhas do mapa de buffer
            for row in cursor:
                #print row[0]
                #criando a expressao de selecao para os buffers
                self.query="FID=%d"%row[0]
                
                #chamando o metodo de selecao de atributos da classe MethodsArcpy
                MethodsArcpy.selecByAtributes(self)
                #chamando o metodo de select by location da classe MethodsArcpy
                MethodsArcpy.selectByLocation(self)
                #chamando o metodo que faz a soma da coluna area do shp de vegetacao que esta selecionado
                self.result_sum=MethodsArcpy.sum_selection(self)
                #arredondando para duas casa o resultado
                self.result_sum=round(self.result_sum,2)
                # criando a linha que sera gravada no txt
                linha=`row[0]`+"	"+`self.result_sum`+"\n"
                #escrevendo a linha                
                self.txt.write(linha)
                
        #fechando o txt
        self.txt.close()
        
#instanciando minha classe
mt=metrica_pai_GAP("clip_buffer10000m_mestrado_gabrielle_100m_explod","buffer_2000m_mestrado_gabrielle")
mt.travels_buffer()
