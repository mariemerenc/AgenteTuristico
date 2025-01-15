# Instalar dependências
install:
	pip install --upgrade pip && \
		pip install -r requirements.txt

# Formatar código
format:
	black *.py

# Preencher o banco de dados
populate-database:
	python populate_database.py

# Iniciar o front-end Streamlit
run-frontend:
	streamlit run app.py

# Atualizar branch do repositório
update-branch:
	git config --global user.name $(USER_NAME) && \
	git config --global user.email $(USER_EMAIL) && \
	git commit -am "Update with new results" && \
	git push --force origin HEAD:update

# Login no Hugging Face
hf-login:
	pip install -U "huggingface_hub[cli]" && \
	git config pull.rebase true && \
	git pull origin update && \
	git switch update && \
	huggingface-cli login --token $(HF) --add-to-git-credential

# Enviar arquivos para o Hugging Face Spaces
push-hub:
	huggingface-cli upload mariemerenc/Agente_de_Turismo ./App --repo-type=space --commit-message="Sync App files" && \
	huggingface-cli upload mariemerenc/Agente_de_Turismo ./Model /Model --repo-type=space --commit-message="Sync Model" 

# Fazer deploy completo
deploy: hf-login push-hub

# Executar o fluxo completo (popular banco, iniciar front-end e etapas adicionais)
all: install format populate-database run-frontend update-branch deploy
