# Troubleshoot

Problemas frequentes encontrados durante o processo de desenvolvimento.

## `.env` parse

- OS: Windows (até o momento)
- Exemplo de erro: `UserWarning: Engine not recognized from url:`

Aparentemente, alguns parsers de `.env` não suportam o uso de aspas (para
definir strings). Por conta disso, na hora de criar o arquivo `.env` pode ser
necessário não usar aspas nem colocar comentários após declarações.

## A aplicação não consegue se comunicar com o servidor, mesmo com a requisição aparecendo no log

Verficar se o _host_ do servidor está adicionado nas variáveis de ambiente (ou `.env`) dentro de `ALLOWED_HOSTS`.

Solução sugerida (recomendável apenas para testes): `ALLOWED_HOSTS=*`
