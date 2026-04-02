import re, requests, json, os, html, time, shutil, subprocess
from urllib.parse import quote

# No topo do arquivo, após os imports:
try:
    with open("/home/micro-3/Portable/key.txt", "r") as f:
        TOKEN = f.read().strip()
except Exception as e:
    print(f"Erro ao ler a chave: {e}")
    TOKEN = ""

def extrair_tag_do_drive(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, timeout=10, headers=headers)
        match = re.search(r"<title>(.*?)</title>", response.text)
        if match:
            titulo_drive = html.unescape(match.group(1)).upper()
            if "DUAL" in titulo_drive:
                return "DUAL"
            if "LEG" in titulo_drive:
                return "LEG"
    except:
        pass
    return "DUB"


def limpar_titulo_final(texto_bruto):
    texto = html.unescape(texto_bruto)
    texto = re.sub(r"<.*?>", " ", texto)
    for trava in ["http", "bit.ly", "is.gd", "Assistir", "Download"]:
        if trava in texto:
            texto = texto.split(trava)[0]
    match_ano = re.search(r"\b(19|20)\d{2}\b", texto)
    if match_ano:
        texto = texto[: match_ano.start()]
    ruido = ["DUAL", "DUB", "LEG", "1080P", "720P", "FULL HD", "REPLAYOUTV", "079"]
    t_up = texto.upper()
    for r in ruido:
        t_up = re.sub(rf"\b{r}\b", "", t_up)
    t_up = re.sub(r"-\d+", "", t_up)
    return " ".join(t_up.replace("-", " ").split()).strip()


def buscar_tmdb(titulo):
    headers = {"Authorization": f"Bearer {TOKEN}"}
    url = f"https://api.themoviedb.org/3/search/movie?query={quote(titulo)}&language=pt-BR"
    try:
        res = requests.get(url, headers=headers, timeout=5).json()
        if res.get("results"):
            return res["results"][0]
    except:
        pass
    return None


def main():
    while True:
        try:
            os.system("clear")
            print("\n" + "=" * 50)
            print("      PAINEL DE CONTROLE DO ACERVO V17.3")
            print("=" * 50)
            print(" [1] Iniciar Lote")
            print(" [2] Deletar Filme")
            print(" [3] Alterar Capa (Manual)")
            print(" [4] Criar Backup Manual")
            print(" [5] Restaurar Backup (.bak)")
            print(" [6] Enviar Links (GitHub)")
            print(" [7] Sair")
            print("=" * 50)

            op = input("Escolha: ").strip()

            if op == "1":
                inicio = time.time()
                # Backup automático antes de processar
                if os.path.exists("links_acervo.js"):
                    shutil.copy("links_acervo.js", "links_acervo.js.bak")
                acervo = []
                if os.path.exists("links_acervo.js"):
                    with open(
                        "links_acervo.js", "r", encoding="utf-8", errors="ignore"
                    ) as f:
                        conteudo = f.read()
                        m = re.search(r"\[.*\]", conteudo, re.DOTALL)
                        if m:
                            acervo = json.loads(m.group(0))

                antigo_total = len(acervo)

                with open("filmes.txt", "r", encoding="utf-8", errors="ignore") as f:
                    linhas = [l.strip() for l in f.readlines() if "http" in l]

                print(
                    f"\n📊 Acervo: {antigo_total} | Novos no lote: {len(linhas)}\n"
                    + "-" * 30
                )

                for i, linha in enumerate(linhas, 1):
                    url_origem = re.search(r'(https?://[^\s"\'<>]+)', linha).group(1)
                    link_final = url_origem
                    if "drive.google.com" not in url_origem:
                        try:
                            r_link = requests.head(
                                url_origem, allow_redirects=True, timeout=10
                            )
                            link_final = r_link.url
                        except:
                            pass

                    tag = extrair_tag_do_drive(link_final)
                    titulo = limpar_titulo_final(linha)
                    filme_data = buscar_tmdb(titulo)
                    capa = (
                        f"https://image.tmdb.org/t/p/w500{filme_data['poster_path']}"
                        if filme_data and filme_data.get("poster_path")
                        else "https://placehold.jp/24/111111/ffffff/300x450.png?text=Sem%20Capa"
                    )
                    ano = (
                        filme_data.get("release_date", "")[:4] if filme_data else "----"
                    )
                    print(f"[{i}/{len(linhas)}] {titulo} | {ano} | {tag}")
                    if not any(item["link"] == link_final for item in acervo):
                        acervo.append(
                            {
                                "t": titulo,
                                "c": capa,
                                "a": ano,
                                "link": link_final,
                                "tags": tag,
                                "n": 1 if "NATAL" in titulo.upper() else 0,
                            }
                        )

                with open("links_acervo.js", "w", encoding="utf-8") as f:
                    f.write(
                        "filmes = "
                        + json.dumps(acervo, indent=4, ensure_ascii=False)
                        + ";"
                    )

                decorrido = time.time() - inicio
                print(f"\n✅ Total no Acervo: {len(acervo)}")
                print(f"✅ Tempo: {int(decorrido//60)}m {int(decorrido%60)}s")
                input("\n[Enter]...")

            elif op == "2":
                termo = input("\nNome para apagar: ").upper()
                if os.path.exists("links_acervo.js"):
                    with open("links_acervo.js", "r", encoding="utf-8") as f:
                        conteudo = f.read()
                        match = re.search(r"\[.*\]", conteudo, re.DOTALL)
                        if match:
                            acervo = json.loads(match.group(0))
                            novos = [f for f in acervo if termo not in f["t"].upper()]
                            with open("links_acervo.js", "w", encoding="utf-8") as f:
                                f.write(
                                    "filmes = "
                                    + json.dumps(novos, indent=4, ensure_ascii=False)
                                    + ";"
                                )
                            print(f"🚀 Removido! (Restantes: {len(novos)})")
                input("\nEnter para voltar...")

            elif op == "3":
                # Carrega o acervo atualizado do arquivo antes de começar
                acervo = []
                if os.path.exists("links_acervo.js"):
                    with open("links_acervo.js", "r", encoding="utf-8") as f:
                        conteudo = f.read()
                        m = re.search(r"\[.*\]", conteudo, re.DOTALL)
                        if m:
                            acervo = json.loads(m.group(0))

                termo = (
                    input("\n🔍 Digite parte do NOME para ALTERAR: ").strip().upper()
                )
                encontrados = [f for f in acervo if termo in f["t"].upper()]

                filme_para_alterar = None
                if not encontrados:
                    print("❌ Nenhum filme encontrado.")
                elif len(encontrados) == 1:
                    filme_para_alterar = encontrados[0]
                    print(f" Filme encontrado: {filme_para_alterar['t']}")
                else:
                    print("\nResultados:")
                    for i, f in enumerate(encontrados):
                        print(f"[{i}] {f['t']} ({f['a']})")
                    escolha = input("\nEscolha o NÚMERO: ").strip()
                    if escolha.isdigit() and int(escolha) < len(encontrados):
                        filme_para_alterar = encontrados[int(escolha)]

                if filme_para_alterar:
                    print(f"\n--- Editando: {filme_para_alterar['t']} ---")
                    print("(ENTER para manter o atual)")

                    n_t = input(f"Título [{filme_para_alterar['t']}]: ").strip().upper()
                    if n_t:
                        filme_para_alterar["t"] = n_t

                    n_a = input(f"Ano [{filme_para_alterar['a']}]: ").strip()
                    if n_a:
                        filme_para_alterar["a"] = n_a

                    n_l = input(f"Link Drive [{filme_para_alterar['link']}]: ").strip()
                    if n_l:
                        filme_para_alterar["link"] = n_l

                    n_tag = (
                        input(f"Tag [{filme_para_alterar['tags']}]: ").strip().upper()
                    )
                    if n_tag:
                        filme_para_alterar["tags"] = n_tag

                    n_c = input(f"Capa [{filme_para_alterar['c']}]: ").strip()
                    if n_c:
                        filme_para_alterar["c"] = n_c

                    with open("links_acervo.js", "w", encoding="utf-8") as f:
                        f.write(
                            "filmes = "
                            + json.dumps(acervo, indent=4, ensure_ascii=False)
                            + ";"
                        )
                    print("\n✅ Atualizado!")

                input("\n[Enter]...")

            elif op == "4":
                if os.path.exists("links_acervo.js"):
                    shutil.copy("links_acervo.js", "links_acervo.js.bak")
                    print("💾 Backup manual criado!")
                input("\nEnter para voltar...")

            elif op == "5":
                if os.path.exists("links_acervo.js.bak"):
                    shutil.copy("links_acervo.js.bak", "links_acervo.js")
                    print("🔄 Backup restaurado com sucesso!")
                else:
                    print("❌ Arquivo .bak não encontrado.")
                input("\nEnter para voltar...")

            elif op == "6":
                print("\n" + "-" * 40)
                print("🚀 ENVIANDO FILMES E SÉRIES PARA O GITHUB")
                print("-" * 40)
                confirmacao = input("Confirmar envio para o GitHub? (s/n): ").lower()

                if confirmacao == "s":
                    try:
                        # 1. Gerar versão baseada na hora atual (Cache Busting)
                        versao_nova = time.strftime('%Y%m%d%H%M')
                        
                        # 2. Atualizar o index.html cirurgicamente (Filmes e Séries)
                        if os.path.exists("index.html"):
                            with open("index.html", "r", encoding="utf-8") as f:
                                conteudo_html = f.read()
                            
                            # Atualiza a versão dos FILMES
                            conteudo_html = re.sub(r'links_acervo\.js\?v=[\d\.]+', f'links_acervo.js?v={versao_nova}', conteudo_html)
                            
                            # Atualiza a versão das SÉRIES (Novo!)
                            conteudo_html = re.sub(r'series_acervo\.js\?v=[\d\.]+', f'series_acervo.js?v={versao_nova}', conteudo_html)
                            
                            with open("index.html", "w", encoding="utf-8") as f:
                                f.write(conteudo_html)
                            print(f"✅ HTML atualizado para v={versao_nova} (Filmes e Séries)")
                        
                        # 3. Prepara os arquivos (Agora incluindo series_acervo.js)
                        print("📦 Selecionando arquivos (index, links, series e pasta img)...")
                        # ADICIONADO: "series_acervo.js" na lista abaixo
                        subprocess.run(["git", "add", "links_acervo.js", "series_acervo.js", "index.html", "img/"], check=True)

                        # 4. Cria o commit com a data e hora
                        mensagem = f"Atualização Total: {time.strftime('%d/%m/%Y %H:%M')}"
                        subprocess.run(["git", "commit", "-m", mensagem], check=True)

                        # 5. Envia para o servidor
                        print("📤 Enviando para o servidor...")
                        subprocess.run(["git", "push", "origin", "main"], check=True)
                        
                        print("-" * 40)
                        print("✅ SUCESSO! TUDO FOI ATUALIZADO NO GITHUB.")
                        
                    except Exception as e:
                        print(f"\n❌ Erro no envio: {e}")
                else:
                    print("\n❌ ENVIO CANCELADO.")
                
                input("\n[Enter] para voltar...")            
            elif op == "7":
                print("Saindo do programa...")
                break

        except Exception as e:
            print(f"❌ Erro inesperado no menu: {e}")
            input("\n[Enter] para continuar...")

if __name__ == "__main__":
    main()
