# desktop-timelapse

Script simples para capturar screenshots periódicos de um monitor escolhido e depois montar um timelapse em vídeo com `ffmpeg`.

## Como funciona

O script [`timelapse.py`](/C:/Projetos/desktop-timelapse/timelapse.py) faz o seguinte:

- pede o intervalo entre capturas em segundos;
- pede o nome da pasta de saída, com padrão `timelapse_frames`;
- lista os monitores disponíveis e permite escolher qual será gravado;
- usa o monitor principal por padrão se nenhuma opção for selecionada;
- salva as imagens em PNG na pasta informada;
- nomeia os arquivos em sequência, como `000001.png`, `000002.png`, `000003.png`;
- permite pausar e retomar a captura com a tecla `P`;
- encerra a execução com `Ctrl + C`.

## Pré-requisitos

- Python 3.10+ instalado
- Dependência Python `mss`
- Windows

O script usa `msvcrt`, então o comportamento atual é específico de Windows.

## Instalação

Instale a dependência necessária:

```powershell
pip install mss
```

## Como executar

Rode o script:

```powershell
python timelapse.py
```

Depois disso, informe no terminal o intervalo entre capturas, em segundos.

Exemplo:

```text
Digite o intervalo entre capturas, em segundos: 5
Digite o nome da pasta de saída [timelapse_frames]:
Monitores disponiveis:
1: 1920x1080 em (0, 0) (principal)
2: 1920x1080 em (1920, 0)
Selecione o monitor para gravar [Enter = principal]:
```

Nesse exemplo, uma imagem será salva a cada 5 segundos na pasta padrão `timelapse_frames`, usando o monitor principal porque o prompt foi deixado em branco.

Se quiser usar outra pasta, basta informar um nome diferente:

```text
Digite o intervalo entre capturas, em segundos: 5
Digite o nome da pasta de saída [timelapse_frames]: reuniao-manha
Monitores disponiveis:
1: 1920x1080 em (0, 0) (principal)
2: 2560x1440 em (-2560, 0)
Selecione o monitor para gravar [Enter = principal]: 2
```

## Controles durante a captura

- `P`: pausa a captura
- `P` novamente: retoma a captura
- `Ctrl + C`: encerra o processo

As imagens são salvas automaticamente na pasta escolhida na execução.

## Gerar o vídeo com ffmpeg

Depois de capturar os frames, gere o vídeo a partir dos arquivos PNG sequenciais.

Se estiver dentro da pasta onde os frames foram salvos, use:

```powershell
..\ffmpeg.exe -framerate 30 -i %06d.png -c:v libx264 -pix_fmt yuv420p timelapse.mp4
```

Se preferir executar a partir da raiz do projeto usando a pasta padrão, use:

```powershell
.\ffmpeg.exe -framerate 30 -i .\timelapse_frames\%06d.png -c:v libx264 -pix_fmt yuv420p timelapse.mp4
```

Se tiver usado outra pasta, ajuste o caminho de entrada. Exemplo:

```powershell
.\ffmpeg.exe -framerate 30 -i .\reuniao-manha\%06d.png -c:v libx264 -pix_fmt yuv420p timelapse.mp4
```

Isso gera o arquivo `timelapse.mp4`.

## Estrutura esperada

Após uma captura, o projeto deve ficar parecido com isto:

```text
desktop-timelapse/
|-- ffmpeg.exe
|-- README.md
|-- timelapse.py
`-- timelapse_frames/
    |-- 000001.png
    |-- 000002.png
    `-- ...
```

## Observações

- O script permite escolher qual monitor sera gravado.
- Se voce pressionar `Enter` no prompt de selecao, o script usa o monitor principal.
- Se você pressionar `Enter` sem informar uma pasta, o script usa `timelapse_frames`.
- Se você rodar o script novamente, novos arquivos continuarão sendo gravados nessa pasta.
