<!-- Logo aqui -->

# CNotes - Server

Neste repositório será gerenciado o desenvolvimento da API do sistema CNotes. Aqui serão armazenado o código, documentação e afins durante todo o desenvolvimento da aplicação.

---

Essa é uma aplicação desenvolvida por meio do [DJango](https://www.djangoproject.com). Sendo inicialmente gerada pelo `django-admin startproject`.

## Build & Run

_TO-DO_

## Documentações

O projeto deve ser documentado no diretório `docs` do repositório, em formato _Markdown_. Lá estarão documentações diversas, desde problemas frequentes até detalhamentos do funcionamento da aplicação e telas.

Documentações dentro do código **não** devem ser substituídas por essas.

## Colaboração

Para colaborar na aplicação será necessário seguir os seguintes requisitos:

### Git

É necessário conhecimento básico sobre o funcionamento do Git e como utilizá-lo. Além disso, o uso de boas práticas de Git é necessário, dentre elas ressalta-se:

1. Commits frequentes e sucintos
2. Uso de branches para qualquer mudança na aplicação
3. Evitar _rebases_ e _force pushes_

### Estilo de código

O projeto usará como linter o `flake8` e o formatador `autopep8`, ambos já colocados como dependências do projeto. É **obrigatório** a execução do `flake8` antes de criar um PR, para evitar inconsistências de formatação.

### Code review

Todo código a ser adicionado na aplicação deve ser antes revisado por ume colega de equipe, a fim de evitar entrada de código defeituoso na aplicação, a colaboração de todos nesse processo de revisão é extremamente importante. Para realizar essa revisão é necessário que toda feature que venha a ser adiciona esteja em uma branch a parte (de preferência com um nome descritivo como: `feature/login`, `fix/validacaoEmail`), que então será mesclada à branch de desenvolvimento por meio de uma _Pull Request_, onde o código será validado e revisado antes de ser enviado.

[Guia: Code-review](https://lontras-e-preguicas.github.io/guides/code-review/)

<!-- ### Estrutura do projeto

A estrutura do projeto está descrita em [structure](docs/structure.md) -->
