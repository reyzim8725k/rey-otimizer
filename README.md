# 🛡️ Rey Optimizer

Painel desktop em Python para diagnóstico, monitoramento e manutenção cuidadosa do Windows, com tema roxo.

> **Estado:** protótipo funcional em desenvolvimento. Teste primeiro em uma máquina virtual.

## Recursos

- Dashboard com CPU, RAM, disco, sistema e uptime.
- Scanner de aplicativos do Registro e Microsoft Store.
- Desinstalação em lote usando os desinstaladores oficiais, com confirmação e lista protegida.
- Ações de manutenção explícitas: TEMP, DNS e ponto de restauração.
- Monitoramento de processos e métricas com `psutil`.
- Logs diários e interface em threads para não travar a UI.

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
