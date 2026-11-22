import pytest

from app.core.security import hash_password, verify_password


def test_hash_no_guarda_la_contrasena_y_se_verifica():
    hash_ = hash_password("Clave1234")
    assert hash_ != "Clave1234"
    assert hash_.startswith("$2b$")  # formato bcrypt
    assert verify_password("Clave1234", hash_)
    assert not verify_password("otra-clave", hash_)


def test_dos_hashes_de_la_misma_contrasena_son_distintos():
    # bcrypt agrega una sal aleatoria a cada hash
    assert hash_password("Clave1234") != hash_password("Clave1234")


def test_contrasena_demasiado_larga_no_provoca_error_500():
    # 40 letras "é" ocupan 80 bytes en UTF-8 (más de los 72 que admite bcrypt)
    larga = "é" * 40
    assert not verify_password(larga, hash_password("Clave1234"))
    with pytest.raises(ValueError):
        hash_password(larga)
