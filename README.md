# 🖨️ Conversor SVG Inteligente para Impressão 3D

O **Conversor SVG Inteligente** é uma aplicação web desenvolvida em Python e Streamlit projetada especificamente para criadores, designers e entusiastas de impressão 3D e personalização. A ferramenta transforma imagens rasterizadas (PNG, JPG, JPEG) em arquivos vetoriais SVG limpos, contornados e perfeitamente otimizados para importação direta em softwares de fatiamento (como Cura, PrusaSlicer, OrcaSlicer) ou ferramentas de modelagem CAD (como Fusion 360 e Tinkercad).

Ao contrário de vetores tradicionais, este conversor isola o conteúdo útil da imagem, elimina blocos quadrados de fundo e gera curvas suavizadas prontas para extrusão volumétrica ou gravação a laser.

---

## 🚀 Funcionalidades

*   **Processamento Inteligente de Fundo:** Identifica e trata os canais de contraste para garantir que o objeto principal seja o vetorizado, isolando o fundo de forma eficiente.
*   **Vetorização Binária de Alta Performance (VTracer):** Utiliza o motor `vtracer` baseado em Rust para extrair contornos precisos usando curvas *spline*, evitando bordas serrilhadas ou pixeladas no fatiador 3D.
*   **Otimização de Memória Pronta para a Nuvem:** Tratamento de buffers de imagem 100% em memória, garantindo velocidade e compatibilidade com servidores Linux sem problemas de permissão de escrita de arquivos temporários.
*   **Interface Simples e Direta:** Upload intuitivo com geração e download nativo do arquivo SVG final em segundos.

---

## 🛠️ Tecnologias Utilizadas

*   **[Python 3.12](https://www.python.org/)** - Linguagem base de alto desempenho para manipulação de dados.
*   **[Streamlit](https://streamlit.io/)** - Framework moderno para a construção e disponibilização da interface web.
*   **[Pillow (PIL)](https://python-pillow.org/)** - Biblioteca analítica para tratamento, binarização e preparação dos canais alfa das imagens.
*   **[VTracer](https://github.com/visioncortex/vtracer)** - Algoritmo de vetorização ultrarrápido baseado em Rust para conversão de raster para vetor.

---

## 💻 Como Executar o Projeto Localmente

### Pré-requisitos
Certifique-se de ter o **Python 3.12** instalado em sua máquina.

1. **Clone o repositório:**
   ```bash
   git clone [https://github.com/ernany92/Conversor-svg-3d.git](https://github.com/ernany92/Conversor-svg-3d.git)
   cd Conversor-svg-3d

# No Windows
python -m venv venv
.\venv\Scripts\activate

# No Linux/macOS
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

streamlit run main.py

Acesse o endereço local indicado no seu terminal (geralmente http://localhost:8501)

#  Desenvolvedor

Ernâny Verruck de Oliveira - GitHub

#  Licença

Este projeto está sob a licença MIT. Sinta-se livre para clonar, modificar e distribuir o código conforme necessário.
