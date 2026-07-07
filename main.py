import streamlit as st
import vtracer
import os
from PIL import Image, ImageOps

# Configuração da página do Streamlit
st.set_page_config(page_title="Conversor SVG para Impressão 3D", page_icon="🖨️", layout="centered")

def otimizar_imagem_universal(imagem_pil):
    """Processa a imagem PIL diretamente na memória para isolar o conteúdo."""
    img = imagem_pil.convert("RGBA")
    w, h = img.size
    
    # Amostra os 4 cantos da imagem
    cantos = [img.getpixel((0, 0)), img.getpixel((w-1, 0)), img.getpixel((0, h-1)), img.getpixel((w-1, h-1))]
    
    luminosidades = []
    for c in cantos:
        if c[3] > 50:
            lum = 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]
            luminosidades.append(lum)
    
    fundo_eh_escuro = len(luminosidades) > 0 and (sum(luminosidades) / len(luminosidades)) < 127
    
    if fundo_eh_escuro:
        base = Image.new("RGBA", img.size, (0, 0, 0, 255))
        base.paste(img, (0, 0), img)
        cinza = base.convert("L")
        imagem_final = ImageOps.invert(cinza)
    else:
        base = Image.new("RGBA", img.size, (255, 255, 255, 255))
        base.paste(img, (0, 0), img)
        imagem_final = base.convert("L")
    
    imagem_binaria = imagem_final.point(lambda x: 0 if x < 140 else 255, '1')
    
    # Salva temporariamente para o vtracer ler
    caminho_temp = "temp_interface_processado.png"
    imagem_binaria.save(caminho_temp)
    return caminho_temp

# --- INTERFACE GRAPHICA ---
st.title("🖨️ Conversor SVG Inteligente para Impressão 3D")
st.write("Transforme qualquer logotipo ou texto em um SVG limpo, sem blocos quadrados de fundo.")

# Componente de Upload de arquivo
arquivo_upload = st.file_uploader("Arraste ou selecione uma imagem (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])

if arquivo_upload is not None:
    # Abre a imagem usando PIL
    imagem_original = Image.open(arquivo_upload)
    
    # Cria duas colunas para mostrar o preview e o resultado
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Sua Imagem")
        st.image(imagem_original, use_container_width=True)
        
    with col2:
        st.subheader("Processamento")
        # Botão para disparar a conversão
        if st.button("🚀 Converter para SVG", use_container_width=True):
            with st.spinner("Vetorizando contornos..."):
                try:
                    # 1. Processa a imagem na memória
                    imagem_temporaria = otimizar_imagem_universal(imagem_original)
                    
                    # 2. Define caminhos de saída
                    nome_original = os.path.splitext(arquivo_upload.name)[0]
                    caminho_svg_saida = f"{nome_original}_pronto_3d.svg"
                    
                    # 3. Executa a vetorização do vtracer
                    vtracer.convert_image_to_svg_py(
                        imagem_temporaria, 
                        caminho_svg_saida, 
                        colormode='binary',
                        mode='spline',       
                        filter_speckle=4,     
                        corner_threshold=60  
                    )
                    
                    # Lendo o arquivo gerado para disponibilizar para o usuário
                    with open(caminho_svg_saida, "rb") as f:
                        dados_svg = f.read()
                    
                    st.success("✅ SVG Gerado com Sucesso!")
                    
                    # Botão nativo de download do Streamlit
                    st.download_button(
                        label="📥 Baixar Arquivo SVG",
                        data=dados_svg,
                        file_name=caminho_svg_saida,
                        mime="image/svg+xml",
                        use_container_width=True
                    )
                    
                    # Limpeza dos arquivos locais criados durante o processo
                    if os.path.exists(imagem_temporaria):
                        os.remove(imagem_temporaria)
                    if os.path.exists(caminho_svg_saida):
                        os.remove(caminho_svg_saida)
                        
                except Exception as e:
                    st.error(f"Erro no processamento: {e}")