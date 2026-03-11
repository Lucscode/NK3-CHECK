@echo off
title NK3 Inventario TI
echo Iniciando o Servidor Local do NK3 Inventario...
echo Por favor, nao feche esta janela preta.
echo ---------------------------------------------------

:: Muda para o diretorio do projeto (onde o .bat est rodando)
cd /d "%~dp0\inventory_api"

:: Verifica se o banco existe, seno pode rodar o init_db
if not exist "inventory.db" (
    echo [INFO] Banco de dados vazio encontrado. Inicializando tabelas base...
    python init_db.py
)

:: Inicia o uvicorn em background (ou foreground para no fechar o terminal)
start /B venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000

:: Aguarda 3 segundos para o servidor subir
timeout /t 3 /nobreak > nul

:: Abre o navegador padrao direto na pagina inicial do app
echo Abrindo o navegador...
start http://127.0.0.1:8000/

:: Mantm o terminal aberto pra mostrar os logs
echo ---------------------------------------------------
echo Sistema online! O navegador foi aberto.
echo Para desligar o sistema, basta fechar *esta* tela preta.
echo ---------------------------------------------------
pause > nul
