#!/usr/bin/python3

import json
import os
import socket
import struct
from typing import Dict, List, Tuple

import paho.mqtt.client as paho


REGISTER_DEFINITIONS = {
    "plant_ems_work_mode": {"address": 30003, "qty": 1, "type": "u16", "scale": 1, "scope": "plant"},
    "plant_grid_sensor_status": {"address": 30004, "qty": 1, "type": "u16", "scale": 1, "scope": "plant"},
    "plant_grid_active_power": {"address": 30005, "qty": 2, "type": "s32", "scale": 1000, "scope": "plant"},
    "plant_on_off_grid_status": {"address": 30009, "qty": 1, "type": "u16", "scale": 1, "scope": "plant"},
    "plant_max_active_power": {"address": 30010, "qty": 2, "type": "u32", "scale": 1000, "scope": "plant"},
    "plant_ess_soc": {"address": 30014, "qty": 1, "type": "u16", "scale": 10, "scope": "plant"},
    "plant_active_power": {"address": 30031, "qty": 2, "type": "s32", "scale": 1000, "scope": "plant"},
    "plant_pv_power": {"address": 30035, "qty": 2, "type": "s32", "scale": 1000, "scope": "plant"},
    "plant_running_state": {"address": 30051, "qty": 1, "type": "u16", "scale": 1, "scope": "plant"},
    "plant_pv_total_generation": {"address": 30088, "qty": 4, "type": "u64", "scale": 100, "scope": "plant"},
    "plant_total_load_daily_consumption": {"address": 30092, "qty": 2, "type": "u32", "scale": 100, "scope": "plant"},
    "plant_total_load_consumption": {"address": 30094, "qty": 4, "type": "u64", "scale": 100, "scope": "plant"},
    "plant_total_imported_energy": {"address": 30260, "qty": 4, "type": "u64", "scale": 100, "scope": "plant"},
    "plant_total_exported_energy": {"address": 30264, "qty": 4, "type": "u64", "scale": 100, "scope": "plant"},
    "inverter_model_type": {"address": 30500, "qty": 15, "type": "string", "scale": 1, "scope": "inverter"},
    "inverter_serial_number": {"address": 30515, "qty": 10, "type": "string", "scale": 1, "scope": "inverter"},
    "inverter_rated_active_power": {"address": 30540, "qty": 2, "type": "u32", "scale": 1000, "scope": "inverter"},
    "inverter_running_state": {"address": 30578, "qty": 1, "type": "u16", "scale": 1, "scope": "inverter"},
    "inverter_active_power": {"address": 30587, "qty": 2, "type": "s32", "scale": 1000, "scope": "inverter"},
    "inverter_reactive_power": {"address": 30589, "qty": 2, "type": "s32", "scale": 1000, "scope": "inverter"},
    "inverter_battery_power": {"address": 30599, "qty": 2, "type": "s32", "scale": 1000, "scope": "inverter"},
    "inverter_battery_soc": {"address": 30601, "qty": 1, "type": "u16", "scale": 10, "scope": "inverter"},
    "inverter_battery_soh": {"address": 30602, "qty": 1, "type": "u16", "scale": 10, "scope": "inverter"},
    "inverter_avg_cell_temperature": {"address": 30603, "qty": 1, "type": "s16", "scale": 10, "scope": "inverter"},
    "inverter_avg_cell_voltage": {"address": 30604, "qty": 1, "type": "u16", "scale": 1000, "scope": "inverter"},
    "inverter_alarm1": {"address": 30605, "qty": 1, "type": "u16", "scale": 1, "scope": "inverter"},
    "inverter_alarm2": {"address": 30606, "qty": 1, "type": "u16", "scale": 1, "scope": "inverter"},
    "inverter_alarm3": {"address": 30607, "qty": 1, "type": "u16", "scale": 1, "scope": "inverter"},
    "inverter_alarm4": {"address": 30608, "qty": 1, "type": "u16", "scale": 1, "scope": "inverter"},
    "inverter_alarm5": {"address": 30609, "qty": 1, "type": "u16", "scale": 1, "scope": "inverter"},
    "inverter_grid_frequency": {"address": 31001, "qty": 1, "type": "u16", "scale": 100, "scope": "inverter"},
    "inverter_output_type": {"address": 31004, "qty": 1, "type": "u16", "scale": 1, "scope": "inverter"},
    "inverter_phase_a_voltage": {"address": 31011, "qty": 2, "type": "u32", "scale": 100, "scope": "inverter"},
    "inverter_phase_b_voltage": {"address": 31013, "qty": 2, "type": "u32", "scale": 100, "scope": "inverter"},
    "inverter_phase_c_voltage": {"address": 31015, "qty": 2, "type": "u32", "scale": 100, "scope": "inverter"},
    "inverter_phase_a_current": {"address": 31017, "qty": 2, "type": "s32", "scale": 100, "scope": "inverter"},
    "inverter_phase_b_current": {"address": 31019, "qty": 2, "type": "s32", "scale": 100, "scope": "inverter"},
    "inverter_phase_c_current": {"address": 31021, "qty": 2, "type": "s32", "scale": 100, "scope": "inverter"},
    "inverter_power_factor": {"address": 31023, "qty": 1, "type": "u16", "scale": 1000, "scope": "inverter"},
    "inverter_pack_count": {"address": 31024, "qty": 1, "type": "u16", "scale": 1, "scope": "inverter"},
    "inverter_pv_string_count": {"address": 31025, "qty": 1, "type": "u16", "scale": 1, "scope": "inverter"},
    "inverter_mppt_count": {"address": 31026, "qty": 1, "type": "u16", "scale": 1, "scope": "inverter"},
    "inverter_pv1_voltage": {"address": 31027, "qty": 1, "type": "s16", "scale": 10, "scope": "inverter"},
    "inverter_pv1_current": {"address": 31028, "qty": 1, "type": "s16", "scale": 100, "scope": "inverter"},
    "inverter_pv2_voltage": {"address": 31029, "qty": 1, "type": "s16", "scale": 10, "scope": "inverter"},
    "inverter_pv2_current": {"address": 31030, "qty": 1, "type": "s16", "scale": 100, "scope": "inverter"},
    "inverter_pv3_voltage": {"address": 31031, "qty": 1, "type": "s16", "scale": 10, "scope": "inverter"},
    "inverter_pv3_current": {"address": 31032, "qty": 1, "type": "s16", "scale": 100, "scope": "inverter"},
    "inverter_pv4_voltage": {"address": 31033, "qty": 1, "type": "s16", "scale": 10, "scope": "inverter"},
    "inverter_pv4_current": {"address": 31034, "qty": 1, "type": "s16", "scale": 100, "scope": "inverter"},
    "inverter_pv_power": {"address": 31035, "qty": 2, "type": "s32", "scale": 1000, "scope": "inverter"},
    "inverter_pv_daily_generation": {"address": 31509, "qty": 2, "type": "u32", "scale": 100, "scope": "inverter"},
    "inverter_pv_total_generation": {"address": 31511, "qty": 2, "type": "u32", "scale": 100, "scope": "inverter"},
}

READ_BLOCKS = {
    "plant": [
        (30003, 12),
        (30031, 6),
        (30051, 1),
        (30260, 8),
    ],
    "inverter": [
        (30500, 25),
        (30540, 14),
        (30578, 32),
        (31509, 4),
    ],
}

DOMOTICZ_POWER_KEYS = {
    "plant_grid_active_power",
    "plant_max_active_power",
    "plant_active_power",
    "plant_pv_power",
    "inverter_rated_active_power",
    "inverter_active_power",
    "inverter_reactive_power",
    "inverter_battery_power",
    "inverter_pv_power",
}


def env_str(name: str, default: str) -> str:
    return os.getenv(name, default).strip()


def env_int(name: str, default: int) -> int:
    return int(env_str(name, str(default)))


def env_float(name: str, default: float) -> float:
    return float(env_str(name, str(default)))


def env_bool(name: str, default: bool) -> bool:
    return env_str(name, "1" if default else "0").lower() in {"1", "true", "yes", "on"}


def load_config() -> Dict[str, object]:
    domoticz_idx_raw = env_str("DOMOTICZ_IDX_MAP", "{}")
    try:
        domoticz_idx = json.loads(domoticz_idx_raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Nieprawidłowy JSON w DOMOTICZ_IDX_MAP: {exc}") from exc

    if not isinstance(domoticz_idx, dict):
        raise RuntimeError("DOMOTICZ_IDX_MAP musi być JSON-em typu object.")

    normalized_idx = {}
    for key, value in domoticz_idx.items():
        try:
            normalized_idx[str(key)] = int(value)
        except (TypeError, ValueError) as exc:
            raise RuntimeError(f"Nieprawidłowy idx dla '{key}': {value}") from exc

    return {
        "host": env_str("SIGENERGY_HOST", "host.docker.internal"),
        "port": env_int("SIGENERGY_PORT", 502),
        "plant_unit_id": env_int("SIGENERGY_PLANT_UNIT_ID", 247),
        "inverter_unit_id": env_int("SIGENERGY_INVERTER_UNIT_ID", 1),
        "timeout_s": env_float("SIGENERGY_TIMEOUT_S", 5.0),
        "poll_interval_s": env_int("POLL_INTERVAL_S", 15),
        "verbose": env_bool("VERBOSE", True),
        "mqtt_enabled": env_bool("MQTT_ENABLED", False),
        "mqtt_server": env_str("MQTT_SERVER", "host.docker.internal"),
        "mqtt_port": env_int("MQTT_PORT", 1883),
        "mqtt_topic": env_str("MQTT_TOPIC", "domoticz/in"),
        "mqtt_username": env_str("MQTT_USERNAME", ""),
        "mqtt_passwd": env_str("MQTT_PASSWORD", ""),
        "domoticz_idx": normalized_idx,
    }


def log(verbose: bool, message: str) -> None:
    if verbose:
        print(message, flush=True)


def decode_registers(raw_registers: List[int], value_type: str, scale: int):
    if value_type == "string":
        payload = bytearray()
        for register in raw_registers:
            payload.extend(struct.pack(">H", register))
        return payload.decode("ascii", errors="ignore").rstrip("\x00 ").strip()

    if value_type == "u16":
        raw_value = raw_registers[0]
    elif value_type == "s16":
        raw_value = struct.unpack(">h", struct.pack(">H", raw_registers[0]))[0]
    elif value_type == "u32":
        raw_value = (raw_registers[0] << 16) | raw_registers[1]
    elif value_type == "s32":
        raw_value = struct.unpack(">i", struct.pack(">HH", raw_registers[0], raw_registers[1]))[0]
    elif value_type == "u64":
        raw_value = (
            (raw_registers[0] << 48)
            | (raw_registers[1] << 32)
            | (raw_registers[2] << 16)
            | raw_registers[3]
        )
    else:
        raise ValueError(f"Unsupported type: {value_type}")

    if scale == 1:
        return raw_value
    return round(raw_value / scale, 3)


def build_mbap(transaction_id: int, unit_id: int, pdu_length: int) -> bytes:
    return struct.pack(">HHHB", transaction_id, 0, pdu_length + 1, unit_id)


def recv_exact(sock: socket.socket, size: int) -> bytes:
    chunks = bytearray()
    while len(chunks) < size:
        chunk = sock.recv(size - len(chunks))
        if not chunk:
            raise RuntimeError("Połączenie zamknięte przez serwer Modbus.")
        chunks.extend(chunk)
    return bytes(chunks)


def read_block(sock: socket.socket, transaction_id: int, unit_id: int, start_address: int, quantity: int, verbose: bool) -> List[int]:
    function_code = 0x03
    pdu = struct.pack(">BHH", function_code, start_address, quantity)
    request = build_mbap(transaction_id, unit_id, len(pdu)) + pdu
    log(verbose, f"[MODBUS] unit={unit_id} addr={start_address} qty={quantity} tx={transaction_id}")
    sock.sendall(request)

    header = recv_exact(sock, 7)
    rx_tid, _proto, length, rx_unit = struct.unpack(">HHHB", header)
    payload = recv_exact(sock, length - 1)

    if rx_tid != transaction_id:
        raise RuntimeError(f"Unexpected transaction id: expected {transaction_id}, got {rx_tid}")
    if rx_unit != unit_id:
        raise RuntimeError(f"Unexpected unit id: expected {unit_id}, got {rx_unit}")

    fc = payload[0]
    if fc & 0x80:
        raise RuntimeError(f"Modbus exception code {payload[1]} dla unit={unit_id}, address={start_address}")
    if fc != function_code:
        raise RuntimeError(f"Unexpected function code: {fc}")

    byte_count = payload[1]
    register_bytes = payload[2 : 2 + byte_count]
    if len(register_bytes) != quantity * 2:
        raise RuntimeError(f"Niepełny blok rejestrów dla address={start_address}: {len(register_bytes)} bajtów")

    return list(struct.unpack(f">{quantity}H", register_bytes))


def collect_values(config: Dict[str, object]) -> Dict[str, object]:
    registers_by_address: Dict[Tuple[str, int], int] = {}
    read_errors: List[str] = []
    transaction_id = 1

    blocks = [
        ("plant", int(config["plant_unit_id"])),
        ("inverter", int(config["inverter_unit_id"])),
    ]

    with socket.create_connection((config["host"], int(config["port"])), timeout=float(config["timeout_s"])) as sock:
        sock.settimeout(float(config["timeout_s"]))
        for scope, unit_id in blocks:
            for start_address, quantity in READ_BLOCKS[scope]:
                try:
                    block_data = read_block(sock, transaction_id, unit_id, start_address, quantity, bool(config["verbose"]))
                    for offset, register_value in enumerate(block_data):
                        registers_by_address[(scope, start_address + offset)] = register_value
                except Exception as exc:
                    read_errors.append(f"{scope}:{unit_id}:{start_address}+{quantity} -> {exc}")
                transaction_id += 1

    values = {}
    for key, definition in REGISTER_DEFINITIONS.items():
        scope = str(definition["scope"])
        address = int(definition["address"])
        quantity = int(definition["qty"])
        register_keys = [(scope, address + offset) for offset in range(quantity)]
        if not all(register_key in registers_by_address for register_key in register_keys):
            continue
        raw_registers = [registers_by_address[register_key] for register_key in register_keys]
        values[key] = decode_registers(raw_registers, str(definition["type"]), int(definition["scale"]))

    values["inverter_total_current"] = round(
        float(values.get("inverter_phase_a_current", 0) or 0)
        + float(values.get("inverter_phase_b_current", 0) or 0)
        + float(values.get("inverter_phase_c_current", 0) or 0),
        2,
    )

    if read_errors:
        values["_read_errors"] = read_errors
    return values


def probe_register(config: Dict[str, object], unit_id: int, address: int, quantity: int) -> bool:
    try:
        with socket.create_connection((config["host"], int(config["port"])), timeout=float(config["timeout_s"])) as sock:
            sock.settimeout(float(config["timeout_s"]))
            read_block(sock, 1, unit_id, address, quantity, False)
        return True
    except Exception:
        return False


def add_optional_blocks(config: Dict[str, object]) -> None:
    plant_unit = int(config["plant_unit_id"])
    inverter_unit = int(config["inverter_unit_id"])

    optional_blocks = [
        ("plant", plant_unit, 30088, 7),
        ("inverter", inverter_unit, 31001, 35),
    ]

    for scope, unit_id, start_address, quantity in optional_blocks:
        if probe_register(config, unit_id, start_address, quantity):
            existing = READ_BLOCKS[scope]
            if (start_address, quantity) not in existing:
                existing.append((start_address, quantity))


def connect_mqtt(config: Dict[str, object]):
    if not config["mqtt_enabled"]:
        return None

    client = paho.Client(client_id=f"sigenergy_{config['inverter_unit_id']}")
    if config["mqtt_username"] or config["mqtt_passwd"]:
        client.username_pw_set(config["mqtt_username"], config["mqtt_passwd"])
    client.connect(config["mqtt_server"], int(config["mqtt_port"]), 60)
    client.loop_start()
    return client


def publish_to_domoticz(client, topic: str, idx: int, value, verbose: bool) -> None:
    if idx <= 0 or client is None:
        return
    payload = json.dumps({"idx": idx, "nvalue": 0, "svalue": str(value)})
    log(verbose, f"[MQTT] topic={topic} payload={payload}")
    client.publish(topic, payload)


def publish_values(config: Dict[str, object], values: Dict[str, object]) -> None:
    mqtt_client = connect_mqtt(config)
    try:
        for key, idx in dict(config["domoticz_idx"]).items():
            if key not in values:
                continue

            value = values[key]
            if key in DOMOTICZ_POWER_KEYS and isinstance(value, (int, float)):
                value = round(float(value) * 1000, 1)

            publish_to_domoticz(mqtt_client, str(config["mqtt_topic"]), int(idx), value, bool(config["verbose"]))
    finally:
        if mqtt_client is not None:
            mqtt_client.loop_stop()
            mqtt_client.disconnect()


def print_value_log(config: Dict[str, object], values: Dict[str, object]) -> None:
    summary_keys = [
        "inverter_model_type",
        "inverter_serial_number",
        "plant_active_power",
        "plant_grid_active_power",
        "plant_pv_power",
        "plant_ess_soc",
        "inverter_active_power",
        "inverter_battery_power",
        "inverter_battery_soc",
        "inverter_grid_frequency",
        "inverter_phase_a_voltage",
        "inverter_phase_b_voltage",
        "inverter_phase_c_voltage",
        "inverter_phase_a_current",
        "inverter_phase_b_current",
        "inverter_phase_c_current",
        "inverter_total_current",
        "inverter_pv1_voltage",
        "inverter_pv1_current",
        "inverter_pv2_voltage",
        "inverter_pv2_current",
        "inverter_pv_power",
        "inverter_pv_daily_generation",
        "inverter_pv_total_generation",
    ]

    print("[PARSED] Odczytane wartości:", flush=True)
    for key in summary_keys:
        if key in values:
            print(f"  {key} = {values[key]}", flush=True)

    if "_read_errors" in values:
        print("[WARN] Niektóre bloki nie zostały odczytane:", flush=True)
        for item in values["_read_errors"]:
            print(f"  {item}", flush=True)

    if config["verbose"]:
        print("[JSON] Pełny wynik:", flush=True)
        print(json.dumps(values, indent=2, ensure_ascii=False, sort_keys=True), flush=True)


def main() -> int:
    try:
        config = load_config()
        add_optional_blocks(config)
        values = collect_values(config)
        print_value_log(config, values)
        publish_values(config, values)
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
