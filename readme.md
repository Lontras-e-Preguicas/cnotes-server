<!-- Logo aqui -->

# CNotes - Server

Neste repositório será gerenciado o desenvolvimento da API do sistema CNotes. Aqui serão armazenados o código, documentação e afins durante todo o desenvolvimento da aplicação.

---

Essa é uma aplicação desenvolvida por meio do [DJango](https://www.djangoproject.com). Sendo inicialmente gerada pelo `django-admin startproject`.

## Build & Run

### Dependências

- Python
- Pipenv
- PostgreSQL (opcional)

### Preparação

- Instalar o `Pipenv`
    - `pip install pipenv`
- Instalar as dependências do projeto
    - `pipenv install --dev`
    - Algumas bibliotecas (como o Pillow) têm dependências no sistema operacional,
    nesse caso é necessário instalá-las de acordo com a documentação da biblioteca.
- Configurar variáveis de ambiente (arquivo `.env`)
    - Referência em `.env.example`

### Execução e testagem

- Primeiramente, ativar o ambiente virtual do Pipenv
    - `pipenv shell`
- Migrações
    - `cd app` (se não estiver no diretório)
    - `python manage.py migrate`
- Execução
    - `cd app` (se não estiver no diretório)
    - `python manage.py runserver`
- Testes
    - `cd app` (se não estiver no diretório)
    - `python manage.py test`

## Documentações

O projeto deve ser documentado no diretório `docs` do repositório, em formato _Markdown_. Lá estarão documentações diversas, desde problemas frequentes até detalhamentos do funcionamento da aplicação e telas.

Documentações dentro do código **não** devem ser substituídas por essas.

## Colaboração

Para colaborar na aplicação será necessário seguir os seguintes requisitos:

### Git

É necessário conhecimento básico sobre o funcionamento do Git e como utilizá-lo. Além disso, o uso de boas práticas de Git é necessário, dentre elas ressaltam-se:

1. Commits frequentes e sucintos
2. Uso de branches para qualquer mudança na aplicação
3. Evitar _rebases_ e _force pushes_

### Estilo de código

O projeto usará como linter o `flake8` e o formatador `autopep8`, ambos já colocados como dependências do projeto. É **obrigatório** a execução do `flake8` antes de criar um PR, para evitar inconsistências de formatação.

### Testes

É necessário desenvolver testes para quaisquer novas funcionalidades adicionadas à aplicação.

Além disso, recomenda-se fortemente a implementação do padrão de desenvolvimento [TDD (Test-driven Development)](https://pt.wikipedia.org/wiki/Test-driven_development). 

### Code review

Todo código a ser adicionado na aplicação deve ser antes revisado por ume colega de equipe, a fim de evitar entrada de código defeituoso na aplicação, a colaboração de todos nesse processo de revisão é extremamente importante. Para realizar essa revisão é necessário que toda feature que venha a ser adiciona esteja em uma branch a parte (de preferência com um nome descritivo como: `feature/login`, `fix/validacaoEmail`), que então será mesclada à branch de desenvolvimento por meio de uma _Pull Request_, onde o código será validado e revisado antes de ser enviado.

[Guia: Code-review](https://lontras-e-preguicas.github.io/guides/code-review/)

### CI (Integração Contínua)

Todos _pushes_ e _pull requests_ para as branches principais do projeto (no momento, só a `dev`) estarão
sujeitos a execução automática de testes para assegurar a qualidade e funcionamento do código.

### Estrutura do projeto

O projeto segue a estrutura padrão do DJango com algumas pequenas alterações, dentre elas:

- Os testes ficam em pacotes a parte, ao invés de um único arquivo `tests.py`
- Os modelos são concentrados no app `core`
- O mantimento ou não do Admin do DJango ainda está em debate
