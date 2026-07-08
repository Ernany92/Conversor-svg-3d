# 🖨️ Conversor SVG Inteligente para Impressão 3D

O Conversor SVG Inteligente é uma aplicação web desenvolvida em **Python** e **Streamlit** projetada especificamente para criadores, designers e entusiastas de impressão 3D e personalização. A ferramenta transforma imagens rasterizadas (PNG, JPG, JPEG) em arquivos SVG limpos, contornados e perfeitamente otimizados para importação direta em softwares de fatiamento (como Bambu Studio, Cura, PrusaSlicer, OrcaSlicer) ou ferramentas de modelagem CAD (como Fusion 360 e Tinkercad).

Ao contrário dos conversores tradicionais, esta ferramenta trata morfologicamente a imagem na memória, elimina blocos quadrados de fundo e gera curvas suavizadas prontas para extrusão volumétrica, corte ou gravação a laser.

---

## 🚀 Funcionalidades

* **Processamento Inteligente de Fundo:** Identifica e trata automaticamente os canais de contraste (identificando fundos claros ou escuros) para garantir que apenas o objeto principal seja vetorizado.
* **Controle de Definição de Bordas (Threshold Dinâmico):** Ajuste fino do ponto de corte do contraste em tempo real, ideal para eliminar sombras, ruídos ou serrilhados do arquivo original.
* **Ajuste de Espessura do Traço (Erosão/Dilatação):** Permite engrossar digitalmente linhas finas (evitando que sumam no fatiador por serem menores que o bocal de 0.4 mm) ou afinar traços muito unidos.
* **Lupa Interativa com Zoom & Pan (Scroll do Mouse):** Interface integrada via JavaScript que permite inspecionar detalhes microscópicos da prévia do traço. Use a **bolinha de rolagem do mouse** para aproximar (até 15x) e clique-e-arraste para navegar pelo desenho.
* **Vetorização Binária de Alta Performance (VTracer):** Utiliza o motor *VTracer* baseado em Rust para extrair contornos precisos usando curvas `spline`, evitando bordas pixeladas no fatiamento.
* **Interface Simples com Prévia em Tempo Real:** Todo o processamento gráfico é exibido instantaneamente na tela conforme você move os controles, garantindo o download do SVG perfeito logo na primeira tentativa.

---

## 🛠️ Tecnologias Utilizadas

* **Python 3.12:** Linguagem base para a manipulação e estruturação dos dados.
* **Streamlit:** Framework moderno para a construção e disponibilização da interface web.
* **OpenCV & NumPy:** Processamento morfológico avançado (binarização, erosão e dilatação de pixels).
* **Pillow (PIL):** Biblioteca para tratamento inicial, isolamento de canais Alfa e preparação de cores.
* **VTracer:** Algoritmo de vetorização ultrarrápido baseado em Rust para conversão cirúrgica de raster para vetor.

---

## 💻 Como Executar o Projeto Localmente

### Pré-requisitos
Certifique-se de ter o Python 3.12 instalado em sua máquina.

### 1. Clonar o Repositório
```bash
git clone [https://github.com/ernany92/Conversor-svg-3d.git](https://github.com/ernany92/Conversor-svg-3d.git)
cd Conversor-svg-3d

2. Configurar o Ambiente Virtual

## No Windows:

DOS
python -m venv venv
.\venv\Scripts\activate
## No Linux/macOS:

Bash
python3 -m venv venv
source venv/bin/activate

3. Instalar as Dependências

Bash
pip install -r requirements.txt

4. Executar a Aplicação

Bash
streamlit run main.py

##  Configuração para Nuvem (Deploy)

Para rodar a aplicação em servidores Linux (como o Streamlit Cloud), certifique-se de que o seu arquivo requirements.txt utilize a versão opencv-python-headless para evitar falhas de inicialização de interface gráfica no servidor.

## Desenvolvedor
Ernâny Verruck de Oliveira - GitHub

## Licença
Este projeto está sob a licença MIT. Sinta-se livre para clonar, modificar e distribuir o código conforme necessário.
