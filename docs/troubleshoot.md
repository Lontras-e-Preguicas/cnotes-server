# Troubleshoot

Problemas frequentes encontrados durante o processo de desenvolvimento.

## `.env` parse

- OS: Windows (até o momento)
- Exemplo de erro: `UserWarning: Engine not recognized from url:`

Aparentemente, alguns parsers de `.env` não suportam o uso de aspas (para
definir strings). Por conta disso, na hora de criar o arquivo `.env` pode ser
necessário não usar aspas nem colocar comentários após declarações.