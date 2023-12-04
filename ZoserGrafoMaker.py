import networkx as nx
import matplotlib.pyplot as plt
from tkinter import *
from tkinter import messagebox, simpledialog, Label, Entry, Checkbutton, IntVar
from tkinter.simpledialog import askstring, askfloat
import easygui


class CustomDialog(simpledialog.Dialog):
    def body(self, master):
        Label(master, text="Peso da Aresta:").grid(row=0)
        Label(master, text="Aresta é Direcionada?").grid(row=1)
        Label(master, text="Nome da Aresta:").grid(row=2)

        self.e1 = Entry(master)
        self.e2_var = IntVar()
        self.e2 = Checkbutton(master, variable=self.e2_var)
        self.e3 = Entry(master)

        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)
        self.e3.grid(row=2, column=1)

        return self.e1 # initial focus

    def apply(self):
        peso = self.e1.get()
        direcionada = self.e2_var.get()
        nome_aresta = self.e3.get()
        self.result = peso, direcionada, nome_aresta



class GrafoApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Zoser Grafo Maker")
        
        self.nome_grafo = StringVar()
        self.nome_grafo.set("Grafo")

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

        self.botao_relatorio = Button(self.master, text="Relatório", command=self.exibir_relatorio)
        self.botao_relatorio.pack(side=LEFT)

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

        dialog = CustomDialog(self.master)
        if dialog.result is None:
            return

        peso, direcionada, nome_aresta = dialog.result

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

    def gerar_grafo_networkx(self):
        G = nx.DiGraph() if self.direcionado else nx.Graph()

        # Adiciona os vértices ao grafo
        for v in self.vertices:
            G.add_node(v)

        # Adiciona as arestas ao grafo
        for v1, v2, estilo in self.arestas:
            G.add_edge(v1, v2, weight=estilo['weight'])

        return G


    def executar_algoritmo(self):
        if not self.grafo.nodes() or not self.grafo.edges():
            messagebox.showinfo("Aviso", "O grafo precisa ter vértices e arestas para executar os algoritmos.")
            return

        algoritmos = ["Prim", "Kruskal", "Componentes Conexos", "Floyd-Warshall", "Ford-Fulkerson", "Hopcroft-Karp", "Encontrar Caminho Mais Curto"]
        algoritmo = easygui.choicebox("Escolha o algoritmo a ser executado:", choices=algoritmos)

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
        elif algoritmo.lower() == "ford-fulkerson":
            self.executar_ford_fulkerson()
        elif algoritmo.lower() == "hopcroft-karp":
            self.executar_hopcroft_karp()
        elif algoritmo.lower() == "encontrar caminho mais curto":
            self.encontrar_caminho_mais_curto()
        else:
            messagebox.showinfo("Aviso", "Algoritmo não reconhecido.")

    def executar_prim(self):
        try:
            pos = nx.spring_layout(self.grafo)
            arvore_geradora_minima_prim = nx.minimum_spanning_tree(self.grafo, algorithm='prim')
            print("Árvore Geradora Mínima (Prim):", arvore_geradora_minima_prim.edges())
            nx.draw_networkx_edges(self.grafo, pos, edgelist=arvore_geradora_minima_prim.edges(), edge_color='r', width=2)
            plt.show()
        except Exception as e:
            messagebox.showinfo("Erro", f"Erro ao executar Prim: {e}")

    def executar_kruskal(self):
        try:
            pos = nx.spring_layout(self.grafo)
            arvore_geradora_minima_kruskal = nx.minimum_spanning_tree(self.grafo.to_undirected(), algorithm='kruskal')
            print("Árvore Geradora Mínima (Kruskal):", arvore_geradora_minima_kruskal.edges())
            nx.draw_networkx_edges(self.grafo, pos, edgelist=arvore_geradora_minima_kruskal.edges(), edge_color='r', width=2)
            plt.show()
        except Exception as e:
            messagebox.showinfo("Erro", f"Erro ao executar Kruskal: {e}")

    def executar_componentes_conexos(self):
        try:
            componentes = list(nx.connected_components(self.grafo.to_undirected()))
            print("Componentes Conexos:", componentes)
            messagebox.showinfo("Componentes Conexos", f"Componentes Conexos: {componentes}")
        except Exception as e:
            messagebox.showinfo("Erro", f"Erro ao executar Componentes Conexos: {e}")

    def executar_floyd_warshall(self):
        try:
            matriz_distancias = nx.floyd_warshall_numpy(self.grafo)
            print("Matriz de Distâncias (Floyd-Warshall):")
            print(matriz_distancias)
            messagebox.showinfo("Floyd-Warshall", f"Matriz de Distâncias:\n{matriz_distancias}")
        except Exception as e:
            messagebox.showinfo("Erro", f"Erro ao executar Floyd-Warshall: {e}")

    def executar_ford_fulkerson(self):
        try:
            # Adicione aqui a implementação do Ford-Fulkerson
            messagebox.showinfo("Aviso", "Ford-Fulkerson ainda não implementado.")
        except Exception as e:
            messagebox.showinfo("Erro", f"Erro ao executar Ford-Fulkerson: {e}")

    def executar_hopcroft_karp(self):
        try:
            if not nx.is_bipartite(self.grafo):
                messagebox.showinfo("Aviso", "Hopcroft-Karp só é aplicável a grafos bipartidos.")
                return

            matching_hopcroft_karp = nx.bipartite.maximum_matching(self.grafo)
            print("Emparelhamento Máximo (Hopcroft-Karp):", matching_hopcroft_karp)
            messagebox.showinfo("Hopcroft-Karp", f"Emparelhamento Máximo (Hopcroft-Karp):\n{matching_hopcroft_karp}")
        except Exception as e:
            messagebox.showinfo("Erro", f"Erro ao executar Hopcroft-Karp: {e}")

    def exibir_relatorio(self):
        relatorio = self.gerar_relatorio()

        # Cria uma nova janela
        janela_relatorio = Toplevel(self.master)
        janela_relatorio.title("Relatório do Grafo")

        # Cria um widget Text e adiciona o relatório
        texto_relatorio = Text(janela_relatorio, wrap="word")
        texto_relatorio.insert("1.0", relatorio)
        texto_relatorio.pack()

        # Desabilita a edição do texto
        texto_relatorio.config(state="disabled")

    def obter_matriz_adjacencia(self):
        matriz_adjacencia = nx.to_numpy_array(self.grafo, nodelist=self.vertices)
        return matriz_adjacencia
    
    def encontrar_caminho_mais_curto(self, v1, v2):
        G = self.gerar_grafo_networkx()
        return nx.shortest_path(G, v1, v2)


    def gerar_relatorio(self):
        relatorio = f"Grafo: {self.nome_grafo.get()}\n"
        relatorio += f"- Número de vértices: {self.grafo.number_of_nodes()}\n"
        relatorio += f"- Número de arestas: {self.grafo.number_of_edges()}\n"
        if self.grafo.is_directed():
        # Para grafos direcionados, verifique a conectividade forte e fraca
            relatorio += f"- Conexo (fortemente): {nx.is_strongly_connected(self.grafo)}\n"
            relatorio += f"- Conexo (fracamente): {nx.is_weakly_connected(self.grafo)}\n"
        else:
            # Para grafos não direcionados, use nx.is_connected
            relatorio += f"- Conexo: {nx.is_connected(self.grafo)}\n"
        
        #relatorio += f"- Cíclico: {nx.is_cyclic(self.grafo)}\n"
        #relatorio += f"- Multigrafo: {nx.is_multigraph(self.grafo)}\n"
        #relatorio += f"- Isomorfo: {nx.is_isomorphic(self.grafo, nx.complete_graph(len(self.grafo)))}\n"
        relatorio += f"- Regular: {nx.is_regular(self.grafo)}\n"
        relatorio += f"- Bipartido: {nx.is_bipartite(self.grafo)}\n"
        relatorio += f"- Não-Direcionado: {not self.grafo.is_directed()}\n"
        relatorio += f"- Desconexo: {nx.is_connected(self.grafo.to_undirected())}\n"
        relatorio += f"- Acíclico: {nx.is_directed_acyclic_graph(self.grafo)}\n"
        relatorio += f"- Árvore: {nx.is_tree(self.grafo)}\n"
        relatorio += f"- Floresta: {nx.is_forest(self.grafo)}\n"
        relatorio += f"- Possui Laços: {nx.number_of_selfloops(self.grafo) > 0}\n"
        relatorio += f"- Plano: {nx.is_planar(self.grafo)}\n"
        relatorio += f"- Ordem: {self.grafo.order()}\n"
        relatorio += f"- Grau Máximo: {max(dict(self.grafo.degree()).values())}\n"
        relatorio += f"- Grau Mínimo: {min(dict(self.grafo.degree()).values())}\n"
        relatorio += f"- Número Cromático: {nx.coloring.greedy_color(self.grafo, strategy='largest_first')}\n"
        relatorio += f"- Densidade: {nx.density(self.grafo)}\n"

        # Adiciona a matriz de adjacência ao relatório
        relatorio += "\nMatriz de Adjacência:\n"
        matriz_adjacencia = self.obter_matriz_adjacencia()
        relatorio += str(matriz_adjacencia)

        return relatorio

if __name__ == "__main__":
    root = Tk()
    app = GrafoApp(root)
    root.mainloop()
