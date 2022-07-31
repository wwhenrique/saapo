from bs4 import BeautifulSoup
from pprint import pprint
import re
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException
from time import time
from getpass import getpass

class Saapo:
    #definição do método contrutor
    def __init__(self):
        self.time_inicio = time()
        self.options = webdriver.ChromeOptions()
        self.options.add_experimental_option("excludeSwitches", ["enable-logging"])
        self.servico = Service(ChromeDriverManager().install())
        self.navegador = webdriver.Chrome(options = self.options, service=self.servico)

    #definição do metodo para inicializar o programa sem precisar ficar chamando outros metodos
    def iniciar(self):
        self.logar_no_site()
        self.avaliacao_simulada()
        self.continuar_execucao()
        self.fechar_selenium()

    def continuar_execucao(self):
        print('\n\nDESEJA CONTINUAR COM OUTRO LOGIN?')
        print('DIGITE "1" PARA CONTINUAR, QUALQUER OUTRA TECLA ENCERRARÁ O PROGRAMA!\n')
        opcao = input('DIGITE: ')

        if opcao == '1':
            self.iniciar()
        else:
            return None

    #metodo para logar no site, não retorna erro caso senha esteja incorreta PRECISA CORRIGIR
    #acessa site, pede os dados (login e seha) e entra no perfil
    def logar_no_site(self):
        print('INICIANDO LOGIN')
        print('*'*50)
        self.navegador.get('https://appintranet.cptm.sp.gov.br/Operacao/SAAPO/Autenticacao/Login')
        self.navegador.find_element(By.ID, 'txtLogin').send_keys(input('Insira seu usuário: '))
        self.navegador.find_element(By.ID, 'Senha').send_keys(input("Insira sua senha: "))
        self.navegador.find_element(By.ID, 'btnAcessar').click()
        sleep(3)
        try:
            self.navegador.find_element(By.ID, 'btnAcessarPerfil').click()
            print('\nLOGADO COM SUCESSO!')
        except NoSuchElementException as e:
            print('\nERRO DE REDE OU LOGIN E SENHA!')
            print('REINICIANDO...\n')
            self.logar_no_site()

        sleep(3)
        try:
            self.navegador.find_element(By.ID, 'mnuAvaliacao')
            print('Perfil carregado')
        except NoSuchElementException as e:
            print('\nERRO AO CARREGAR PERFIL!')
            print('REINICIANDO...\n')
            self.logar_no_site()



    #metodo responsavel por toda parte de avaliação
    #eu deveria separar em metodos auxiliares, mas deu preguiça
    def avaliacao_simulada(self):

        for repeat in range(1,4):
            print(f'\nINICIANDO AVALIAÇÃO SIMULADA {repeat} de 3')
            print('*'*50)
            self.navegador.get('https://appintranet.cptm.sp.gov.br/Operacao/SAAPO/AvaliacaoMontagem#BLOQUEIO')
            self.navegador.find_element(By.ID, 'btnMontar').click()

            while True:
                sleep(3)
                try:
                    self.navegador.find_element(By.ID, 'ui-id-1')
                    print('Página de avalição carregada!')
                    webdriver.ActionChains(self.navegador).send_keys(Keys.ESCAPE).perform()
                    break
                except NoSuchElementException as e:
                    print('Esperando carregar avaliação')
                    continue

            html = self.navegador.page_source
            bs = BeautifulSoup(html, 'html.parser')

            questoes = bs.find_all('div', {'id': re.compile(r'ui-accordion-1-panel-')})

            inputs = []
            for questao in questoes:
                a = []
                alternativas = questao.find_all('input')
                for alternativa in alternativas:
                    a.append(alternativa.attrs['value'])

                inputs.append(a)

            click_questoes = self.navegador.find_elements(By.CSS_SELECTOR, '[id^=ui-accordion-1-header-]')
            for i in range(len(questoes)):
                if i == 0:
                    print('Respondendo a questão:', i + 1)
                    sleep(1)
                if i > 0:
                    click_questoes[i].click()
                    print('Respondendo a questão:', i + 1)
                    sleep(1)
                self.navegador.find_element(By.XPATH, f'//*[@value="{min(inputs[i])}"]').click()
                sleep(1)


            #aqui é definido um tempo de espera para finalizar a avaliação
            #necessario para não gerar desconfiança com avaliações rapidas demais
            tempo_espera = 60
            print(f'\nAguardando {tempo_espera} segundos para concluir a avaliação!')
            sleep(tempo_espera)
            self.navegador.find_element(By.ID, 'btnFinalizar').click()

            while True:
                sleep(5)
                try:
                    self.navegador.find_element(By.ID, 'tblResultado')
                    webdriver.ActionChains(self.navegador).send_keys(Keys.ESCAPE).perform()
                    print('\nAvaliação finalizada com sucesso!')
                    break
                except NoSuchElementException as e:
                    print('Aguardando Gabarito')


    def fechar_selenium(self):
        self.navegador.quit()
        print('PROGRAMA ENCERRADO')

saapo = Saapo()
saapo.iniciar()
quit()


