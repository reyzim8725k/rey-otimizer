# 🛡️ Rey Optimizer

![Rey Optimizer](assets/rey-optimizer-banner.png)

Painel desktop em Python para diagnóstico, monitoramento e manutenção cuidadosa do Windows, com tema roxo.

> **Estado:** protótipo funcional em desenvolvimento. Teste primeiro em uma máquina virtual.

## Recursos

- Dashboard com CPU, RAM, disco, sistema e uptime.
- Monitoramento com cartões de uso e gráficos em tempo real para CPU, RAM, disco e rede.
- Scanner de aplicativos do Registro e Microsoft Store.
- Desinstalação em lote usando os desinstaladores oficiais, com confirmação e lista protegida.
- Lista visual de aplicativos com logo, versão, editor e tamanho estimado.
- Ações de manutenção explícitas: TEMP, DNS e ponto de restauração.
- Monitoramento de processos e métricas com `psutil`.
- Logs diários e interface em threads para não travar a UI.
- Logo e ícone oficiais incluídos em `assets/rey-optimizer-logo.png` e `assets/rey-optimizer.ico`.

## Executável pronto pelo GitHub Actions

Cada push na branch `main` executa o workflow **Build Rey Optimizer Windows** em um runner Windows. O workflow valida o código, gera `Rey Optimizer.exe` com manifesto UAC e ícone, e publica o executável e um ZIP na aba **Actions > Artifacts**.

Para criar uma release pública, use uma tag:

```bash
git tag v1.0.0
git push origin v1.0.0
```

Nesse caso, o workflow também cria uma GitHub Release com os arquivos anexados.

## Requisitos e instalação

Windows 10/11 64-bit, Python 3.10+ e permissões administrativas para ações que exigem UAC.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

## Gerar executável

```powershell
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --uac-admin --name "Rey Optimizer" main.py
```

## Segurança

O programa não apaga pastas arbitrárias nem força remoção de aplicativos protegidos. Toda ação destrutiva pede confirmação. Crie backup e ponto de restauração, revise os itens selecionados e não execute em computadores de terceiros sem autorização.

## Estrutura

```text
main.py
core/  # scanner, monitor, logger, admin e engines
ui/    # interface principal
assets/
.github/workflows/build.yml
```

## Roadmap

- [x] Dashboard e monitoramento básico
- [x] Scanner de Registro e Store
- [x] Logs e confirmações
- [ ] Gráficos matplotlib refinados
- [ ] Exportação CSV/JSON na UI
- [ ] Instalador assinado

## Licença

MIT. Veja [LICENSE](LICENSE).

## Autor

Rey — contribuições são bem-vindas via pull request.
