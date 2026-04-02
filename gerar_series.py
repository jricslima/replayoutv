import os
import re

def gerar_js_series():
    series_totais = []

    # 1. Carregando do arquivo .js
    if os.path.exists("series_acervo.js"):
        with open("series_acervo.js", "r", encoding="utf-8") as js_f:
            conteudo = js_f.read()
            series_totais = re.findall(r'\{.*?\}', conteudo, re.DOTALL)
    
    print(f"\n--- Gerenciador de Séries ({len(series_totais)} no acervo) ---")
    print("1. Adicionar novas (do arquivo 'series_site')")
    print("2. Alterar uma série existente")
    print("3. Deletar uma série")
    print("4. Sair")
    
    opcao = input("\nEscolha uma opção: ").strip()

    # --- OPÇÃO 1: ADICIONAR ---
    if opcao == "1":
        if os.path.exists("series_site"):
            with open("series_site", "r", encoding="utf-8") as f:
                for linha in f:
                    partes = [p.strip() for p in linha.split('\t') if p.strip()]
                    if len(partes) >= 3:
                        t, l_p, l_i = partes[0], partes[1], partes[2]
                        item = f'{{ "t": "{t}", "c": "{l_i}", "link": "{l_p}" }}'
                        if item not in series_totais:
                            series_totais.append(item)
            print("✅ Importação concluída.")
        else:
            print("❌ 'series_site' não encontrado.")

    # --- OPÇÃO 2: ALTERAR ---
    elif opcao == "2":
        busca = input("Digite o nome para buscar: ").strip().lower()
        encontradas = [s for s in series_totais if busca in s.lower()]
        if encontradas:
            for i, s in enumerate(encontradas):
                print(f"[{i}] {s}")
            
            escolha = input("\nDigite o NÚMERO para ALTERAR: ").strip()
            if escolha.isdigit():
                idx = int(escolha)
                original = encontradas[idx]
                
                t_at = (re.search(r'"t": "(.*?)"', original) or [None, ""])[1]
                c_at = (re.search(r'"c": "(.*?)"', original) or [None, ""])[1]
                l_at = (re.search(r'"link": "(.*?)"', original) or [None, ""])[1]

                print("\n(Enter para manter o atual)")
                nt = input(f"Título [{t_at}]: ").strip() or t_at
                nc = input(f"Capa [{c_at}]: ").strip() or c_at
                nl = input(f"Link [{l_at}]: ").strip() or l_at

                novo = f'{{ "t": "{nt}", "c": "{nc}", "link": "{nl}" }}'
                series_totais[series_totais.index(original)] = novo
                print("✅ Alterado!")
        else: print("❌ Não encontrado.")

    # --- OPÇÃO 3: DELETAR ---
    elif opcao == "3":
        busca = input("Digite o nome para DELETAR: ").strip().lower()
        encontradas = [s for s in series_totais if busca in s.lower()]
        
        if encontradas:
            for i, s in enumerate(encontradas):
                print(f"[{i}] {s}")
            
            # PROTEÇÃO: Só tenta converter se o usuário realmente digitar um número
            escolha = input("\nDigite o NÚMERO para EXCLUIR: ").strip()
            
            if escolha.isdigit():
                idx = int(escolha)
                if 0 <= idx < len(encontradas):
                    if input(f"Confirmar exclusão? (s/n): ").lower() == 's':
                        series_totais.remove(encontradas[idx])
                        print("🗑️ Removido!")
                else:
                    print("❌ Número fora da lista.")
            else:
                print("❌ Operação cancelada ou número inválido.")
        else:
            print("❌ Nenhuma série encontrada.")

    # Gravação Final
    if opcao in ["1", "2", "3"]:
        with open("series_acervo.js", "w", encoding="utf-8") as js_file:
            js_file.write("var series = [\n    ")
            js_file.write(",\n    ".join(series_totais))
            js_file.write("\n];")
        print(f"💾 Arquivo atualizado! Total: {len(series_totais)}")

if __name__ == "__main__":
    gerar_js_series()
