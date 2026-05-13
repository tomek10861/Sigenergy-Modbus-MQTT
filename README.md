# Sigenergy Modbus MQTT

Integracja do lokalnego odczytu danych z systemu energii Sigenergy przez Modbus TCP. Aplikacja cyklicznie odpytuje rejestry instalacji i falownika, a wyniki może publikować przez MQTT, np. do Domoticz.

## Dla jakiego urządzenia?

Projekt jest przeznaczony dla urządzeń **Sigenergy** udostępniających dane przez **Modbus TCP**. Obsługiwane są odczyty na poziomie całej instalacji oraz konkretnego falownika.

Domyślna konfiguracja komunikacji:

- Modbus TCP: port `5502`,
- plant unit id: `247`,
- inverter unit id: `1`.

## Funkcje

- odczyt danych instalacji i falownika przez Modbus TCP,
- dekodowanie wartości `u16`, `s16`, `u32`, `s32`, `u64` oraz tekstowych,
- obsługa najważniejszych parametrów PV, sieci i baterii,
- opcjonalna publikacja danych do MQTT,
- mapowanie wybranych pomiarów na urządzenia Domoticz,
- uruchamianie w Dockerze.

## Odczytywane dane

Skrypt obsługuje m.in.:

- moc PV,
- moc czynną instalacji,
- moc pobieraną lub oddawaną do sieci,
- stan naładowania baterii,
- moc baterii,
- napięcia i prądy fazowe,
- częstotliwość sieci,
- dzienną i całkowitą produkcję energii,
- model i numer seryjny falownika.

## Struktura projektu

```text
.
├── LICENSE
├── README.md
└── sigenergy_tcp
    ├── Dockerfile
    ├── docker-compose.yml
    ├── entrypoint.sh
    ├── requirements.txt
    └── src
        └── SigenergyInverterData.py
```

## Wymagania

- Docker,
- Docker Compose,
- dostęp sieciowy do urządzenia lub bramki Sigenergy z włączonym Modbus TCP,
- opcjonalnie broker MQTT, jeżeli chcesz publikować dane dalej.

## Konfiguracja

Konfiguracja znajduje się w `sigenergy_tcp/docker-compose.yml`.

Najważniejsze zmienne:

| Zmienna | Opis | Domyślnie |
| --- | --- | --- |
| `SIGENERGY_HOST` | host lub adres IP urządzenia Modbus TCP | `host.docker.internal` |
| `SIGENERGY_PORT` | port Modbus TCP | `5502` |
| `SIGENERGY_PLANT_UNIT_ID` | adres jednostki instalacji | `247` |
| `SIGENERGY_INVERTER_UNIT_ID` | adres jednostki falownika | `1` |
| `SIGENERGY_TIMEOUT_S` | timeout połączenia w sekundach | `5` |
| `POLL_INTERVAL_S` | odstęp między odczytami | `15` |
| `MQTT_ENABLED` | włączenie publikacji MQTT, `1` albo `0` | `0` |
| `MQTT_SERVER` | adres brokera MQTT | `host.docker.internal` |
| `MQTT_PORT` | port brokera MQTT | `1883` |
| `MQTT_TOPIC` | temat MQTT dla Domoticz | `domoticz/in` |
| `MQTT_USERNAME` | użytkownik MQTT | puste |
| `MQTT_PASSWORD` | hasło MQTT | puste |
| `DOMOTICZ_IDX_MAP` | mapowanie pomiarów na IDX-y Domoticz | wszystkie `0` |

## Uruchomienie

```bash
cd sigenergy_tcp
docker compose up -d --build
```

Podgląd logów:

```bash
docker compose logs -f
```

Zatrzymanie:

```bash
docker compose down
```

## Domoticz

Publikacja do Domoticz odbywa się przez MQTT. W `DOMOTICZ_IDX_MAP` ustaw IDX tylko dla tych pomiarów, które chcesz wysyłać. Wartość `0` oznacza pominięcie danego pomiaru.

Przykład:

```yaml
DOMOTICZ_IDX_MAP: |
  {
    "plant_active_power": 101,
    "plant_grid_active_power": 102,
    "plant_pv_power": 103,
    "plant_ess_soc": 104
  }
```

## Licencja

Projekt jest udostępniony na licencji MIT. Szczegóły znajdują się w pliku `LICENSE`.

## English

Sigenergy Modbus MQTT is a local Python and Docker integration for reading Sigenergy inverter and plant data over Modbus TCP. It can optionally publish selected measurements to MQTT, including Domoticz-compatible messages.
