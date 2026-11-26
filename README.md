# Programação de canais no GitHub

Este pacote prepara uma atualização automática, a cada 5 minutos, da programação indicada por `guia` em `canals.json`. O GitHub Actions não permite agendamento automático a cada 1 minuto; 5 minutos é o menor intervalo aceito. O app LG consulta apenas o arquivo pronto `programacao.json`; não faz chamadas ao MeuGuia nem à ponte do PC.

## Instalação no repositório `canalr94`

1. Extraia este pacote na pasta local do repositório `canalr94`.
2. Confirme que o script está em `scripts/update_programacao.py` e o fluxo em `.github/workflows/update-programacao.yml`.
3. Adicione `"guia": "https://meuguia.tv/programacao/canal/CODIGO"` em cada canal que tiver uma página de programação. O `id` de cada canal precisa ser único e estável.
4. Envie os arquivos ao GitHub. No repositório, abra **Actions** e execute **Atualizar programação dos canais** uma vez para conferir o primeiro resultado.
5. Se o GitHub bloquear o `git push` do fluxo, em **Settings > Actions > General > Workflow permissions**, selecione permissão de leitura e escrita para o repositório e salve.

O fluxo cria/atualiza `programacao.json` na raiz. Se nenhuma página responder, ele falha e preserva o arquivo publicado anteriormente. Canais sem `guia` continuam aparecendo normalmente, só sem a linha de programação.

## Exemplo de canal

```json
{
  "id": 1,
  "nome": "TV Brasil",
  "categoria": "TV pública",
  "capa": "",
  "embed": "<iframe src=\"https://exemplo.com/player\" allowfullscreen></iframe>",
  "guia": "https://meuguia.tv/programacao/canal/CODIGO"
}
```

O valor de `guia` deve ser a página de programação daquele canal. Não coloque o iframe do player nesse campo.

## Teste manual opcional

Com Python 3 instalado, abra um terminal na raiz de `canalr94` e execute:

```sh
python scripts/update_programacao.py
```

Não são necessárias bibliotecas extras. O arquivo gerado é compatível com o endereço permanente já configurado no app: `https://raw.githubusercontent.com/renanfigueredo94/canalr94/main/programacao.json`.
