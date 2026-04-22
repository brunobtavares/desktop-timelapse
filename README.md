# Desktop Timelapse

Script simples para capturar screenshots periodicos de um monitor no Windows e, depois, transformar esses frames em um timelapse.

O projeto tem duas etapas separadas:

1. capturar os frames com Python;
2. gerar o video com FFmpeg.

Voce consegue usar a captura apenas com Python e a biblioteca `mss`. O FFmpeg so e necessario na etapa de montar o arquivo `.mp4`.

## O que o script faz

O script [`timelapse.py`](/C:/Projetos/desktop-timelapse/timelapse.py):

- pede o intervalo entre capturas em segundos;
- pede o nome da pasta de saida, com padrao `timelapse_frames`;
- lista os monitores disponiveis;
- permite escolher qual monitor sera gravado;
- usa o monitor principal por padrao se voce pressionar `Enter`;
- salva as imagens em PNG;
- nomeia os arquivos em sequencia, como `000001.png`, `000002.png`, `000003.png`;
- permite pausar e retomar com `P`;
- encerra com `Ctrl + C`.

## Pre-requisitos

Para capturar os frames:

- Windows
- Python 3.10 ou superior
- biblioteca Python `mss`

Para gerar o video depois:

- FFmpeg instalado no sistema ou um `ffmpeg.exe` baixado manualmente

Observacao importante: clonar este repositorio nao instala nem inclui automaticamente o FFmpeg. Se voce quiser gerar o video, precisa configurar isso separadamente.

## Instalacao

Instale a dependencia Python:

```powershell
pip install mss
```

Se quiser gerar o video com FFmpeg depois, voce tem dois caminhos possiveis:

### Opcao 1: FFmpeg instalado no PATH

Instale o FFmpeg no Windows e deixe o comando `ffmpeg` disponivel no terminal.

Depois disso, voce podera usar comandos como:

```powershell
ffmpeg -version
```

Se esse comando responder com a versao do FFmpeg, a configuracao esta pronta.

### Opcao 2: ffmpeg.exe local na raiz do projeto

Se preferir, baixe o binario do FFmpeg manualmente e coloque o arquivo `ffmpeg.exe` dentro da pasta raiz do projeto, no mesmo nivel de `README.md` e `timelapse.py`.

Nesse caso, os comandos de geracao de video devem usar `.\ffmpeg.exe`.

## Como capturar os frames

Execute:

```powershell
python timelapse.py
```

O script vai pedir:

1. o intervalo entre capturas;
2. o nome da pasta de saida;
3. o monitor que sera gravado.

Exemplo usando a pasta padrao e o monitor principal:

```text
Digite o intervalo entre capturas, em segundos: 5
Digite o nome da pasta de saída [timelapse_frames]:
Monitores disponiveis:
1: 1920x1080 em (0, 0) (principal)
2: 1920x1080 em (1920, 0)
Selecione o monitor para gravar [Enter = principal]:
```

Nesse caso:

- os frames vao para a pasta `timelapse_frames`;
- o monitor principal sera usado;
- uma imagem sera salva a cada 5 segundos.

Exemplo escolhendo outra pasta e outro monitor:

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

Os PNGs sao salvos automaticamente na pasta escolhida.

## Como gerar o video

Depois de capturar os frames, voce pode transformar os PNGs em um arquivo `.mp4`.

### Se voce instalou o FFmpeg no PATH

Usando a pasta padrao `timelapse_frames` a partir da raiz do projeto:

```powershell
ffmpeg -framerate 30 -i .\timelapse_frames\%06d.png -c:v libx264 -pix_fmt yuv420p timelapse.mp4
```

Usando uma pasta personalizada, por exemplo `reuniao-manha`:

```powershell
ffmpeg -framerate 30 -i .\reuniao-manha\%06d.png -c:v libx264 -pix_fmt yuv420p timelapse.mp4
```

### Se voce baixou um ffmpeg.exe para a raiz do projeto

Usando a pasta padrao `timelapse_frames`:

```powershell
.\ffmpeg.exe -framerate 30 -i .\timelapse_frames\%06d.png -c:v libx264 -pix_fmt yuv420p timelapse.mp4
```

Usando uma pasta personalizada:

```powershell
.\ffmpeg.exe -framerate 30 -i .\reuniao-manha\%06d.png -c:v libx264 -pix_fmt yuv420p timelapse.mp4
```

Esses comandos geram o arquivo `timelapse.mp4` na pasta atual.

## Estrutura esperada

Depois de uma captura usando a pasta padrao, a estrutura fica parecida com isto:

```text
desktop-timelapse/
|-- README.md
|-- timelapse.py
`-- timelapse_frames/
    |-- 000001.png
    |-- 000002.png
    `-- ...
```

Se voce optar pelo segundo fluxo de FFmpeg, o `ffmpeg.exe` tambem pode ficar na raiz do projeto:

```text
desktop-timelapse/
|-- ffmpeg.exe
|-- README.md
|-- timelapse.py
`-- timelapse_frames/
```

## Resumo rapido

- Para capturar os frames, basta instalar `mss` e rodar `python timelapse.py`.
- Para gerar o video, voce tambem precisa do FFmpeg.
- O FFmpeg pode estar no `PATH` ou como `ffmpeg.exe` na raiz do projeto.
- Se voce nao escolher um monitor, o script usa o monitor principal.
