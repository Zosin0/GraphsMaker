import networkx as nx
import matplotlib.pyplot as plt
from tkinter import *
from tkinter import messagebox
from tkinter.simpledialog import askstring, askfloat

class GrafoApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Grafo App")

        self.grafo = nx.DiGraph()  # Agora usando um grafo direcionado
        self.pos = {}
        self.vertices = []
        self.arestas = []

        self.canvas = Canvas(self.master, width=600, height=600, bg='white')
        self.canvas.pack()

        self.botao_adicionar_vertice = Button(self.master, text="Adicionar Vértice", command=self.habilitar_adicao_vertice)
        self.botao_adicionar_vertice.pack(side=LEFT)

        self.botao_adicionar_aresta = Button(self.master, text="Adicionar Aresta", command=self.habilitar_adicao_aresta)
        self.botao_adicionar_aresta.pack(side=LEFT)

        self.botao_executar_algoritmo = Button(self.master, text="Executar Algoritmo", command=self.executar_algoritmo)
        self.botao_executar_algoritmo.pack(side=LEFT)

        self.habilitar_adicao_vertice()

    def habilitar_adicao_vertice(self):
        self.canvas.bind("<Button-1>", self.adicionar_vertice)
        self.canvas.unbind("<ButtonRelease-1>")

    def habilitar_adicao_aresta(self):
        if len(self.vertices) < 2:
            messagebox.showinfo("Aviso", "Adicione pelo menos dois vértices antes de criar uma aresta.")
            return

        self.canvas.bind("<Button-1>", self.selecionar_vertice_aresta)
        self.canvas.unbind("<ButtonRelease-1>")

    def adicionar_vertice(self, event):
        self.canvas.unbind("<Button-1>")
        nome_vertice = askstring("Nome do Vértice", "Insira o nome do vértice:")
        if nome_vertice:
            x, y = event.x, event.y
            self.vertices.append(nome_vertice)
            self.pos[nome_vertice] = (x, y)

            self.grafo.add_node(nome_vertice, pos=(x, y), nome=nome_vertice)
            self.desenhar_grafo()
        self.habilitar_adicao_vertice()

    def selecionar_vertice_aresta(self, event):
        x, y = event.x, event.y
        vertice_selecionado = None

        for vertice, (vx, vy) in self.pos.items():
            distancia = ((x - vx) ** 2 + (y - vy) ** 2) ** 0.5
            if distancia <= 20:  # Raio do círculo do vértice
                vertice_selecionado = vertice
                break

        if vertice_selecionado is not None:
            if len(self.arestas) % 2 == 0:
                self.arestas.append(vertice_selecionado)
            else:
                self.arestas.append(vertice_selecionado)
                self.adicionar_aresta()
                self.arestas = []
                self.habilitar_adicao_aresta()

    def adicionar_aresta(self):
        v1, v2 = self.arestas
        if self.grafo.has_edge(v1, v2):
            messagebox.showinfo("Aviso", f"A aresta entre {v1} e {v2} já existe.")
            return

        peso = askfloat("Peso da Aresta", "Insira o peso da aresta (deixe em branco para nenhum):", minvalue=0)
        direcionada = messagebox.askyesno("Aresta Direcionada", "A aresta é direcionada?")
        nome_aresta = askstring("Nome da Aresta", "Insira o nome da aresta (opcional):")

        estilo = {'weight': peso or "", 'directed': direcionada, 'nome': nome_aresta}
        self.arestas.append((v1, v2, estilo))
        self.grafo.add_edge(v1, v2, **estilo)

        self.desenhar_grafo()

    def desenhar_grafo(self):
        self.canvas.delete("all")

        for v1, v2, dados in self.grafo.edges(data=True):
            x1, y1 = self.pos[v1]
            x2, y2 = self.pos[v2]
            xc, yc = (x1 + x2) / 2, (y1 + y2) / 2  # Centro da aresta

            if v1 == v2:
                # Aresta de laço (origem e destino iguais)
                self.canvas.create_oval(x1 , y1 - 30, x1 + 30, y1 + 30, outline="black", tags="arestas")
                self.canvas.create_line(x1 + 20, y1, x1 + 30, y1, arrow="last", tags="arestas")
            else:
                # Aresta normal
                if dados['directed']:
                    # Aresta direcionada: desenhe duas linhas com uma seta no centro
                    self.canvas.create_line(x1, y1, xc, yc, width=2, arrow="last", tags="arestas")
                    self.canvas.create_line(xc, yc, x2, y2, width=2, tags="arestas")
                else:
                    # Aresta não direcionada: desenhe uma única linha
                    self.canvas.create_line(x1, y1, x2, y2, width=2, tags="arestas")

            # Adiciona informações da aresta
            texto_aresta = f"{dados['nome']}\n" if dados.get('nome') else ''
            texto_aresta += f"Peso: {dados['weight']}\n" if dados['weight'] else ''
            texto_aresta += "\n" if dados['directed'] else "\n"
            yc_text = yc - 20  # Ajusta a posição y do texto
            self.canvas.create_text(xc, yc_text, text=texto_aresta, font=("Helvetica", 8, "italic"))

        for vertice, (x, y) in self.pos.items():
            # Desenha o vértice
            self.canvas.create_oval(x - 20, y - 20, x + 20, y + 20, fill="white", outline="black", tags="vertices")

            # Adiciona informações do vértice
            self.canvas.create_text(x, y, text=str(vertice), font=("Helvetica", 10, "bold"), tags="vertices")

    # def executar_algoritmo(self):
    #     if not self.grafo.nodes() or not self.grafo.edges():
    #         messagebox.showinfo("Aviso", "O grafo precisa ter vértices e arestas para executar os algoritmos.")
    #         return
    def executar_algoritmo(self):
        if not self.grafo.nodes() or not self.grafo.edges():
            messagebox.showinfo("Aviso", "O grafo precisa ter vértices e arestas para executar os algoritmos.")
            return

        algoritmo = askstring("Escolha o Algoritmo", "Escolha o algoritmo a ser executado:\nPrim, Kruskal, Componentes Conexos, Floyd-Warshall")
        if not algoritmo:
            return

        if algoritmo.lower() == "prim":
            self.executar_prim()
        elif algoritmo.lower() == "kruskal":
            self.executar_kruskal()
        elif algoritmo.lower() == "componentes conexos":
            self.executar_componentes_conexos()
        elif algoritmo.lower() == "floyd-warshall":
            self.executar_floyd_warshall()
        # Adicione mais opções conforme necessário

    def executar_prim(self):
        # Exemplo: Prim
        try:
            pos = nx.spring_layout(self.grafo)
            arvore_geradora_minima_prim = nx.minimum_spanning_tree(self.grafo, algorithm='prim')
            print("Árvore Geradora Mínima (Prim):", arvore_geradora_minima_prim.edges())
            nx.draw_networkx_edges(self.grafo, pos, edgelist=arvore_geradora_minima_prim.edges(), edge_color='r', width=2)
            plt.show()
        except Exception as e:
            messagebox.showinfo("Erro", f"Erro ao executar Prim: {e}")

    def executar_kruskal(self):
        # Exemplo: Kruskal
        try:
            pos = nx.spring_layout(self.grafo)
            arvore_geradora_minima_kruskal = nx.minimum_spanning_tree(self.grafo.to_undirected(), algorithm='kruskal')
            print("Árvore Geradora Mínima (Kruskal):", arvore_geradora_minima_kruskal.edges())
            nx.draw_networkx_edges(self.grafo, pos, edgelist=arvore_geradora_minima_kruskal.edges(), edge_color='r', width=2)
            plt.show()
        except Exception as e:
            messagebox.showinfo("Erro", f"Erro ao executar Kruskal: {e}")

    def executar_componentes_conexos(self):
        # Exemplo: Componentes Conexos
        try:
            componentes = list(nx.connected_components(self.grafo.to_undirected()))
            print("Componentes Conexos:", componentes)
            messagebox.showinfo("Componentes Conexos", f"Componentes Conexos: {componentes}")
        except Exception as e:
            messagebox.showinfo("Erro", f"Erro ao executar Componentes Conexos: {e}")

    def executar_floyd_warshall(self):
        # Exemplo: Floyd-Warshall
        try:
            matriz_distancias = nx.floyd_warshall_numpy(self.grafo)
            print("Matriz de Distâncias (Floyd-Warshall):")
            print(matriz_distancias)
            messagebox.showinfo("Floyd-Warshall", f"Matriz de Distâncias:\n{matriz_distancias}")
        except Exception as e:
            messagebox.showinfo("Erro", f"Erro ao executar Floyd-Warshall: {e}")

    # Adicione mais funções de execução de algoritmos conforme necessário


if __name__ == "__main__":
    root = Tk()
    app = GrafoApp(root)
    root.mainloop()
