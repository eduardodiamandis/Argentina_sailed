# 🇦🇷 Projeto Argentina - Processamento de Dados

Sistema automatizado para download, processamento e atualização de dados de navios da Argentina.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Uso](#uso)
- [Arquitetura](#arquitetura)
- [Melhorias Implementadas](#melhorias-implementadas)

## 🎯 Visão Geral

Este projeto automatiza o processo de:
1. **Download** de planilhas Excel de navios (Sailed e Line-Up)
2. **Processamento** dos dados baixados
3. **Atualização** do banco de dados local
4. **Notificação** por email em caso de erros

## 📁 Estrutura do Projeto

```
argentina_project/
│
├── config/                      # Configurações
│   ├── __init__.py
│   └── settings.py             # Todas as configurações centralizadas
│
├── modules/                     # Módulos principais
│   ├── __init__.py
│   ├── downloader.py           # Download e processamento de arquivos
│   └── data_processor.py       # Processamento e concatenação de dados
│
├── utils/                       # Utilitários
│   ├── __init__.py
│   ├── logger.py               # Configuração de logging
│   └── file_utils.py           # Utilitários para arquivos
│
├── main.py                      # Script principal
├── requirements.txt             # Dependências
├── .env.example                # Exemplo de variáveis de ambiente
└── README.md                   # Este arquivo
```

## 🚀 Instalação

### 1. Clonar/Copiar o projeto

```bash
# Copie todos os arquivos para o diretório desejado
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o arquivo .env com suas credenciais
# GMAIL_USER=seu_email@gmail.com
# GMAIL_APP_PASSWORD=sua_senha_de_app
```

**Nota:** Para gerar uma senha de app do Gmail:
1. Acesse https://myaccount.google.com/security
2. Ative a verificação em duas etapas
3. Vá em "Senhas de app" e gere uma nova senha

## ⚙️ Configuração

Todas as configurações estão centralizadas em `config/settings.py`:

```python
# Diretórios
BASE_DIR = Path.home() / "Desktop" / "Argentina"
SAILED_DIR = BASE_DIR / "Sailed" / "backup"

# URLs
SAILED_URL = "https://boletines.nabsa.com.ar/..."
LINEUP_URL = "https://boletines.nabsa.com.ar/..."

# Timeouts
SAILED_TIMEOUT = 40
LINEUP_TIMEOUT = 18

# Email
EMAIL_RECIPIENTS = ["email1@exemplo.com", "email2@exemplo.com"]
```

Para modificar qualquer configuração, edite apenas o arquivo `settings.py`.

## 💻 Uso

### Executar o processo completo

```bash
python main.py
```

### Executar apenas o download de Sailed

```python
from modules.downloader import process_file
from config.settings import SAILED_URL, SAILED_VESSEL_DIR, SAILED_TIMEOUT

process_file(
    url=SAILED_URL,
    file_name="vessels_sailed_update.xlsx",
    destination_path=SAILED_VESSEL_DIR,
    timeout=SAILED_TIMEOUT
)
```

### Executar apenas a atualização do banco

```python
from modules.data_processor import update_database

update_database()
```

## 🏗️ Arquitetura

### Módulos Principais

#### 1. **config/settings.py**
- Centraliza todas as configurações
- Garante que diretórios existam
- Carrega variáveis de ambiente

#### 2. **utils/logger.py**
- Configura logging com rotação de arquivos
- Envia emails automaticamente em caso de erro
- Handler customizado para emails

#### 3. **utils/file_utils.py**
- Busca arquivo mais recente em diretório
- Gerencia criação de diretórios
- Remove arquivos de forma segura

#### 4. **modules/downloader.py**
- Abre URLs no navegador
- Aguarda download de arquivos
- Processa e salva Excel com data no nome
- Classe `FileDownloader` encapsula toda a lógica

#### 5. **modules/data_processor.py**
- Remove linhas vazias
- Calcula dias desde última atualização
- Concatena dados evitando duplicações mensais
- Adiciona colunas Month e Year
- Classe `DataProcessor` encapsula toda a lógica

#### 6. **main.py**
- Orquestra o processo completo
- Trata erros de forma isolada
- Gera resumo de execução
- Retorna códigos de saída apropriados

### Fluxo de Execução

```
main.py
   │
   ├─> process_sailed_data()
   │     ├─> downloader.process_file()
   │     │     ├─> open_url()
   │     │     ├─> wait_for_download()
   │     │     ├─> read Excel
   │     │     └─> save_excel()
   │     │
   │     └─> data_processor.update_database()
   │           ├─> read database
   │           ├─> get_latest_file()
   │           ├─> remove_trailing_empty_rows()
   │           ├─> concatenate_data()
   │           └─> save updated database
   │
   └─> process_lineup_data()
         └─> downloader.process_file()
```

## ✨ Melhorias Implementadas

### 🎯 Organização
- ✅ **Estrutura modular** com separação clara de responsabilidades
- ✅ **Configurações centralizadas** em um único arquivo
- ✅ **Imports limpos** sem dependências circulares

### 🔧 Código
- ✅ **Classes** para encapsular lógica (FileDownloader, DataProcessor)
- ✅ **Type hints** em todas as funções
- ✅ **Docstrings** completas e padronizadas
- ✅ **Tratamento de erros** robusto com logging detalhado
- ✅ **Uso de Path** ao invés de strings para caminhos
- ✅ **Validações** em todas as operações críticas

### 📊 Logging
- ✅ **Logger consistente** em todos os módulos
- ✅ **Níveis apropriados** (INFO, WARNING, ERROR)
- ✅ **Rotação automática** de arquivos de log
- ✅ **Email automático** em caso de erro
- ✅ **Logs informativos** sobre o progresso

### 🛡️ Robustez
- ✅ **Verificação de existência** de arquivos e diretórios
- ✅ **Criação automática** de diretórios necessários
- ✅ **Tratamento de timeout** no download
- ✅ **Limpeza de arquivos temporários**
- ✅ **Códigos de saída** apropriados para automação

### 📈 Funcionalidades
- ✅ **Estatísticas detalhadas** de processamento
- ✅ **Resumo de execução** ao final
- ✅ **Prevenção de duplicatas** por mês/ano
- ✅ **Suporte a múltiplas planilhas** no mesmo arquivo
- ✅ **Configuração fácil** via arquivo único

## 🔍 Comparação: Antes vs Depois

### Antes ❌
- Configurações espalhadas em múltiplos arquivos
- Paths hardcoded
- Logger com nomes inconsistentes
- Código duplicado
- Sem validações adequadas
- Difícil de testar e manter

### Depois ✅
- Configurações centralizadas em `settings.py`
- Paths configuráveis via variáveis
- Logger único e consistente
- Código DRY (Don't Repeat Yourself)
- Validações em todas operações
- Fácil de testar e manter
- Documentação completa
- Arquitetura escalável

## 🐛 Solução de Problemas

### Email não está sendo enviado
- Verifique se o `.env` está configurado corretamente
- Confirme que a senha de app foi gerada no Gmail
- Verifique os logs para mais detalhes

### Arquivo não está sendo baixado
- Aumente o timeout em `settings.py`
- Verifique se a URL está correta
- Confirme que o nome do arquivo está correto

### Banco de dados não atualiza
- Verifique se o arquivo existe em `Arg_sailed_database.xlsx`
- Confirme que há arquivos na pasta `sailed_vessel`
- Verifique os logs para erros específicos

## 📝 Notas

- Os logs são salvos em `~/Desktop/Argentina/Sailed/backup/logs/`
- Os arquivos são baixados para `~/Downloads/` temporariamente
- O banco atualizado é salvo como `Arg_sailed_database_AT.xlsx`
- Emails são enviados apenas em caso de erro (nível ERROR)

## 🤝 Contribuindo

Para adicionar novas funcionalidades:
1. Adicione configurações em `config/settings.py`
2. Crie módulos em `modules/` ou utilitários em `utils/`
3. Atualize o `main.py` se necessário
4. Documente as mudanças neste README

---

**Desenvolvido com ❤️ para automação de processos**
