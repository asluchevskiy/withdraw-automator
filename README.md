# withdraw-automator
Automate withdraw funds from multiple wallets

## Формат файла

В файле `wallets.csv` таблица со следующими столбцами:
* `private_key` приватный ключ кошелька с которого переводить
* `to_address` адрес назначения
* `networks` сети через запятую (`ethereum|polygon|binance|avalanche|fantom|arbitrum one|arbitrum nova|optimism`)

## Режимы работы

Делаем копию файла `config.py` в `local_config.py`

`TOKEN_CONTRACT = '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174'` -- Адрес контракта токена, если пустая строка или `None` то используется нативный токен сети (ETH, MATIC,. ..)

`WITHDRAW_PERCENT = (30, 80)` -- Диапазон процента баланса, который выводим

`WITHDRAW_AMOUNT_KEEP = (0.1, 0.1)` -- Диапазон баланса, который оставляем

`WITHDRAW_AMOUNT = (1, 1.5)` -- Диапазон баланса, который переводим

`MODE = Mode.ALL` -- Режим работы, допустимые значения `Model.ALL | Mode.PERCENT | Mode.KEEP | Mode.AMOUNT`, названия говорят сами за себя

