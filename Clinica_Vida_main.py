import sqlite3

# --- 1. MÓDULO DE BANCO DE DADOS E FUNÇÕES AUXILIARES ---

# Nome do arquivo do banco de dados
DB_NAME = 'clinica_vida.db'

def conectar_bd():
    """Cria e retorna a conexão com o banco de dados."""
    return sqlite3.connect(DB_NAME)

def criar_tabela():
    """Cria a tabela de pacientes se ela não existir."""
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pacientes (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            idade INTEGER NOT NULL,
            telefone TEXT
        )
    """)
    conn.commit()
    conn.close()

def popular_dados_iniciais():
    """Insere alguns pacientes no BD como exemplo (povoamento)."""
    conn = conectar_bd()
    cursor = conn.cursor()

    dados_iniciais = [
        ('Maria Santos', 30, '(21) 98765-4321'),
        ('João Silva', 45, '(11) 99999-9999'),
        ('Pedro Alves', 72, '(31) 91111-2222'),
        ('Ana Costa', 18, '(47) 90000-0000')
    ]

    # Verifica se a tabela já possui dados para evitar duplicidade no povoamento
    cursor.execute("SELECT COUNT(*) FROM pacientes")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO pacientes (nome, idade, telefone) VALUES (?, ?, ?)", dados_iniciais)
        conn.commit()
        print(f"\n[INFO] {len(dados_iniciais)} pacientes iniciais inseridos no banco de dados.")

    conn.close()

def cadastrar_paciente_bd(nome, idade, telefone):
    """Insere um novo paciente no banco de dados."""
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO pacientes (nome, idade, telefone) VALUES (?, ?, ?)", (nome, idade, telefone))
    conn.commit()
    conn.close()

def obter_todos_pacientes():
    """Retorna todos os pacientes cadastrados."""
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT nome, idade, telefone FROM pacientes ORDER BY nome")
    pacientes = cursor.fetchall()
    conn.close()
    return pacientes

def calcular_estatisticas_bd():
    """Calcula as estatísticas de pacientes (total, média, mais novo/velho)."""
    conn = conectar_bd()
    cursor = conn.cursor()

    # Número total de pacientes
    cursor.execute("SELECT COUNT(*) FROM pacientes")
    total = cursor.fetchone()[0]

    if total == 0:
        conn.close()
        return 0, 0, None, None  # total, media, mais_novo, mais_velho

    # Idade média
    cursor.execute("SELECT AVG(idade) FROM pacientes")
    media = cursor.fetchone()[0]

    # Paciente mais novo (Nome e Idade)
    cursor.execute("SELECT nome, idade FROM pacientes ORDER BY idade ASC LIMIT 1")
    mais_novo = cursor.fetchone()

    # Paciente mais velho (Nome e Idade)
    cursor.execute("SELECT nome, idade FROM pacientes ORDER BY idade DESC LIMIT 1")
    mais_velho = cursor.fetchone()

    conn.close()
    return total, media, mais_novo, mais_velho

def buscar_paciente_bd(nome_busca):
    """Busca um paciente pelo nome, ignorando maiúsculas/minúsculas."""
    conn = conectar_bd()
    cursor = conn.cursor()
    # Usa LIKE com % (wildcard) para buscar nomes que contenham a string
    cursor.execute("SELECT nome, idade, telefone FROM pacientes WHERE nome LIKE ?", ('%' + nome_busca + '%',))
    pacientes_encontrados = cursor.fetchall()
    conn.close()
    return pacientes_encontrados

# --- 2. FUNÇÕES DO MENU ---
def exibir_menu():
    """Exibe o menu de navegação."""
    print("\n" + "=" * 28)
    print("=== SISTEMA CLÍNICA VIDA+ ===")
    print("=" * 28)
    print("1. Cadastrar paciente")
    print("2. Ver estatísticas")
    print("3. Buscar paciente")
    print("4. Listar todos os pacientes")
    print("5. Sair")
    print("-" * 28)

def cadastrar_paciente():
    """RF01: Permite cadastrar um novo paciente."""
    print("\n--- CADASTRO DE PACIENTE ---")
    nome = input("Nome do paciente: ").strip()

    # RNF02: Tratamento de erro para Idade
    while True:
        try:
            idade = int(input("Idade: "))
            if idade <= 0:
                print("A idade deve ser um número positivo.")
                continue
            break
        except ValueError:
            print("Erro! Por favor, digite a idade como um número inteiro válido.")

    telefone = input("Telefone: ").strip()

    if nome and idade:
        cadastrar_paciente_bd(nome, idade, telefone)
        print("Paciente cadastrado com sucesso!")
    else:
        print("Erro: Nome e Idade são campos obrigatórios.")

def ver_estatisticas():
    """RF02: Calcula e exibe estatísticas básicas."""
    print("\n--- ESTATÍSTICAS DA CLÍNICA ---")

    total, media, mais_novo, mais_velho = calcular_estatisticas_bd()

    if total == 0:
        print("Não há pacientes cadastrados para calcular as estatísticas.")
        return

    print(f"Número total de pacientes cadastrados: {total}")
    print(f"Idade média dos pacientes: {media:.2f} anos")

    # Exibe o paciente mais novo e mais velho, se existirem
    if mais_novo:
        print(f"Paciente mais novo: {mais_novo[0]} ({mais_novo[1]} anos)")
    if mais_velho:
        print(f"Paciente mais velho: {mais_velho[0]} ({mais_velho[1]} anos)")

def buscar_paciente():
    """RF03: Permite buscar um paciente pelo nome."""
    print("\n--- BUSCA DE PACIENTE ---")
    nome_busca = input("Digite o nome ou parte do nome do paciente: ").strip()

    if not nome_busca:
        print("A busca não pode ser vazia.")
        return

    resultados = buscar_paciente_bd(nome_busca)

    if resultados:
        print(f"\nPacientes encontrados ({len(resultados)}):")
        # RNF05: Exibir de forma organizada
        print("-" * 40)
        print(f"| {'Nome':<20} | {'Idade':<5} | {'Telefone':<10} |")
        print("-" * 40)
        for nome, idade, telefone in resultados:
            print(f"| {nome:<20} | {idade:<5} | {telefone:<10} |")
        print("-" * 40)
    else:
        print(f"Nenhum paciente encontrado com o nome ou parte do nome '{nome_busca}'.")

def listar_pacientes():
    """RF04: Exibe todos os pacientes cadastrados."""
    print("\n--- LISTA DE TODOS OS PACIENTES ---")
    pacientes = obter_todos_pacientes()

    if not pacientes:
        print("Não há pacientes cadastrados no momento.")
        return

    # RNF05: Exibir de forma organizada
    print("-" * 40)
    print(f"| {'Nome':<20} | {'Idade':<5} | {'Telefone':<10} |")
    print("-" * 40)
    for nome, idade, telefone in pacientes:
        print(f"| {nome:<20} | {idade:<5} | {telefone:<10} |")
    print("-" * 40)

# --- 3. MÓDULO PRINCIPAL (LOOP) ---
def main():
    """Função principal que executa o programa em loop."""
    # Inicialização: Cria a tabela e insere dados de exemplo
    criar_tabela()
    popular_dados_iniciais()

    # RNF03: O programa deve funcionar em loop até o usuário escolher sair
    while True:
        exibir_menu()

        # RNF02: Tratamento de erro para escolha do menu
        try:
            opcao = int(input("Escolha uma opção: "))
        except ValueError:
            print("Opção inválida. Por favor, digite um número de 1 a 5.")
            continue

        if opcao == 1:
            cadastrar_paciente()
        elif opcao == 2:
            ver_estatisticas()
        elif opcao == 3:
            buscar_paciente()
        elif opcao == 4:
            listar_pacientes()
        elif opcao == 5:
            # RF06: Opção de sair
            print("\nObrigado por usar o Sistema Clínica Vida+. Encerrando...")
            break
        else:
            print("Opção inválida. Por favor, escolha uma opção entre 1 e 5.")

if __name__ == "__main__":
    main()