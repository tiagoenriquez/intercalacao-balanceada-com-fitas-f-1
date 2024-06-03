from io import TextIOWrapper
from os import unlink


class Fita:

    def __init__(self, numero) -> None:
        self._numero = numero
        self._nome = f"arquivo-{numero}.txt"
        self._grupos: list[str] = []
        self._registro = ""
        self._posicao = 0
    
    @property
    def numero(self) -> int:
        return self._numero

    @property
    def nome(self) -> str:
        return self._nome
    
    @property 
    def grupos(self) -> list[str]:
        return self._grupos
    
    @property
    def registro(self) -> str:
        return self._registro

    @property
    def registros(self) -> int:
        registros = 0
        for grupo in self._grupos:
            registros += grupo
        if self.registro != "":
            registros += 1
        return registros
    
    @property
    def vazio(self) -> bool:
        if self.registros == 0:
            return True
        return False
    
    def inserir_grupo(self, grupo: str) -> None:
        with open(self._nome, "a") as fita:
            fita.write(grupo)
        self._grupos.append(len(grupo))
    
    def limpar_para_escrita(self) -> None:
        with open(self._nome, "w") as fita:
            fita.write("")
        self._grupos = []
    
    def ler(self) -> None:
        if self._grupos[0] > 0:
            with open(self._nome, "r") as fita:
                fita.seek(self._posicao)
                self._registro = fita.read(1)
                self._posicao += 1
            self._grupos[0] -= 1
        else:
            self._registro = ""
    
    def escrever(self, registro: str) -> None:
        with open(self._nome, "a") as fita:
            fita.write(registro)
        if len(self._grupos) == 0:
            self._grupos.append(1)
        else:
            self._grupos[0] += 1
    
    def remover_primeiro_grupo(self) -> None:
        del self._grupos[0]

    def _transferir_para_saida(self) -> None:
        with open("fita-de-saida.txt", "w") as saida:
            saida.write("")
        for i in range(self.registros):
            with open(self._nome, "r") as temporario:
                temporario.seek(i)
                caractere = temporario.read(1)
                with open("fita-de-saida.txt", "a") as saida:
                    saida.write(f"{caractere} ")
    
    def apagar(self) -> None:
        if self.registros > 0:
            self._transferir_para_saida()
        unlink(self._nome)


class Ordenacao:

    def __init__(self, fita: TextIOWrapper, capacidade: int, unidades: int) -> None:
        self._entrada = fita
        self._capacidade = capacidade
        self._unidades = unidades
        self._ordenados = 0
        self._get_tamanho()
        self._fitas: list[Fita] = []
        self._criar_fitas_temporarias()
        self._ordenar()
        self._intercalar()
        self._apagar_temporarios()
    
    def _get_tamanho(self) -> None:
        self._entrada.seek(0, 2)
        self._tamanho = self._entrada.tell() / 2
        self._entrada.seek(0)

    def _criar_fitas_temporarias(self) -> None:
        for unidade in range(self._unidades):
            self._fitas.append(Fita(unidade + 1))

    def _ordenar(self) -> None:
        fita = 0
        while self._ordenados < self._tamanho:
            grupo = self._entrada.read(self._capacidade * 2).split(' ')[:self._capacidade]
            grupo.sort()
            self._fitas[fita % (self._unidades - 1)].inserir_grupo(''.join(grupo))
            self._ordenados += len(grupo)
            fita += 1
    
    def _vazio(self) -> int:
        for fita in self._fitas:
            if fita.vazio:
                return fita.numero - 1
        return -1
    
    def _preparar_para_escrita(self) -> int:
        em_escrita = self._vazio()
        self._fitas[em_escrita].limpar_para_escrita()
        self._ler_fitas(em_escrita)
        self._fitas[em_escrita].limpar_para_escrita()
        return em_escrita        
    
    def _vazios(self) -> int:
        vazios = 0
        for fita in self._fitas:
            if fita.vazio:
                vazios += 1
        return vazios
    
    def _ler_fitas(self, em_escrita: int) -> None:
        for i in range(len(self._fitas)):
            if i != em_escrita:
                self._fitas[i].ler()
    
    def _sem_registro(self) -> None:
        for fita in self._fitas:
            if fita.registro == "" and fita.vazio:
                return fita.numero - 1
        return -1
    
    def _menor(self) -> str:
        indice = 0
        menor = self._fitas[indice].registro
        for i in range(len(self._fitas)):
            registro = self._fitas[i].registro
            if (registro != "" and registro <= menor) or menor == "":
                indice = i
                menor = registro
        self._fitas[indice].ler()
        return menor

    def _em_leitura_vazios(self, em_escrita: int) -> bool:
        vazios = 0
        for fita in self._fitas:
            if fita.registro != em_escrita + 1 and fita.grupos[0] == 0 and fita.registro == "":
                vazios += 1
        return vazios == self._unidades - 1
    
    def _remover_primeiros_grupos_de_fitas(self, em_escrita: int) -> None:
        for i in range(len(self._fitas)):
            if i != em_escrita:
                self._fitas[i].remover_primeiro_grupo()
    
    def _intercalar(self) -> None:
        em_escrita = self._preparar_para_escrita()
        while self._vazios() != self._unidades - 1:
            self._fitas[em_escrita].escrever(self._menor())
            if self._em_leitura_vazios(em_escrita) and self._vazios() != self._unidades - 1:
                self._remover_primeiros_grupos_de_fitas(em_escrita)
                em_escrita = self._preparar_para_escrita()
    
    def _apagar_temporarios(self) -> None:
        for fita in self._fitas:
            fita.apagar()


with open("fita-de-entrada.txt", "r") as fita:
    Ordenacao(fita, 3, 6)