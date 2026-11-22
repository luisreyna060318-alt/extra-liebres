"""Pruebas de autorización por rol y administración de usuarios (HU-01.3 y HU-01.4)."""

from tests.conftest import encabezado_de

# ---------- HU-01.3 Hacer solo lo que mi rol permite ----------


def test_hu_01_3_sin_sesion_el_listado_de_usuarios_da_401(client):
    assert client.get("/api/usuarios").status_code == 401


def test_hu_01_3_capturista_no_puede_listar_usuarios_403(client, capturista):
    r = client.get("/api/usuarios", headers=encabezado_de(capturista))
    assert r.status_code == 403


def test_hu_01_3_capturista_no_puede_cambiar_roles_ni_siquiera_el_suyo_403(client, capturista):
    r = client.patch(f"/api/usuarios/{capturista.id}", json={"rol": "administrador"}, headers=encabezado_de(capturista))
    assert r.status_code == 403


def test_hu_01_3_el_403_no_cambia_ningun_dato(client, db, capturista):
    client.patch(f"/api/usuarios/{capturista.id}", json={"rol": "administrador"}, headers=encabezado_de(capturista))
    db.refresh(capturista)
    assert capturista.rol == "capturista"


# ---------- HU-01.4 Administrar usuarios y roles ----------


def test_hu_01_4_admin_lista_usuarios_con_total_y_paginacion(client, admin, crear_usuario):
    for i in range(12):
        crear_usuario(f"persona{i:02d}@correo.com", nombre=f"Persona {i:02d}")
    pagina1 = client.get("/api/usuarios", headers=encabezado_de(admin)).json()
    assert pagina1["total"] == 13  # 12 + el admin
    assert len(pagina1["items"]) == 10
    assert pagina1["page"] == 1 and pagina1["size"] == 10

    pagina2 = client.get("/api/usuarios?page=2", headers=encabezado_de(admin)).json()
    assert len(pagina2["items"]) == 3


def test_hu_01_4_el_listado_nunca_incluye_el_hash_de_la_contrasena(client, admin):
    cuerpo = client.get("/api/usuarios", headers=encabezado_de(admin)).text
    assert "password" not in cuerpo


def test_hu_01_4_admin_busca_por_nombre_o_correo_y_filtra_por_rol(client, admin, crear_usuario):
    crear_usuario("lucia@correo.com", nombre="Lucía Pérez")
    crear_usuario("mario@otro.mx", nombre="Mario Gómez")
    encabezado = encabezado_de(admin)

    por_nombre = client.get("/api/usuarios?q=lucía", headers=encabezado).json()
    assert [u["correo"] for u in por_nombre["items"]] == ["lucia@correo.com"]

    por_correo = client.get("/api/usuarios?q=otro.mx", headers=encabezado).json()
    assert [u["correo"] for u in por_correo["items"]] == ["mario@otro.mx"]

    solo_admins = client.get("/api/usuarios?rol=administrador", headers=encabezado).json()
    assert solo_admins["total"] == 1


def test_hu_01_4_paginacion_con_valores_invalidos_da_422(client, admin):
    assert client.get("/api/usuarios?page=0", headers=encabezado_de(admin)).status_code == 422
    assert client.get("/api/usuarios?size=51", headers=encabezado_de(admin)).status_code == 422


def test_hu_01_4_el_cambio_de_rol_se_aplica_en_la_siguiente_peticion(client, admin, capturista):
    encabezado_capturista = encabezado_de(capturista)
    assert client.get("/api/usuarios", headers=encabezado_capturista).status_code == 403

    r = client.patch(f"/api/usuarios/{capturista.id}", json={"rol": "administrador"}, headers=encabezado_de(admin))
    assert r.status_code == 200
    assert r.json()["rol"] == "administrador"

    # Con el MISMO token de antes, ahora sí tiene permiso (el rol se lee de la BD en cada petición)
    assert client.get("/api/usuarios", headers=encabezado_capturista).status_code == 200


def test_hu_01_4_suspender_una_cuenta_le_impide_entrar_y_conserva_sus_datos(client, db, admin, capturista):
    r = client.patch(f"/api/usuarios/{capturista.id}", json={"activo": False}, headers=encabezado_de(admin))
    assert r.status_code == 200 and r.json()["activo"] is False

    login = client.post("/api/auth/login", data={"username": "capturista@correo.com", "password": "Clave1234"})
    assert login.status_code == 403
    assert db.get(type(capturista), capturista.id) is not None  # la cuenta sigue existiendo


def test_hu_01_4_no_se_puede_quitar_el_rol_al_unico_administrador_activo(client, admin):
    r = client.patch(f"/api/usuarios/{admin.id}", json={"rol": "capturista"}, headers=encabezado_de(admin))
    assert r.status_code == 409
    assert "administrador activo" in r.json()["detail"]


def test_hu_01_4_no_se_puede_suspender_al_unico_administrador_activo(client, admin):
    r = client.patch(f"/api/usuarios/{admin.id}", json={"activo": False}, headers=encabezado_de(admin))
    assert r.status_code == 409


def test_hu_01_4_con_dos_administradores_uno_si_puede_dejar_de_serlo(client, admin, crear_usuario):
    otro = crear_usuario("otro-admin@correo.com", rol="administrador")
    r = client.patch(f"/api/usuarios/{admin.id}", json={"rol": "capturista"}, headers=encabezado_de(otro))
    assert r.status_code == 200


def test_hu_01_4_un_administrador_suspendido_no_cuenta_como_activo(client, crear_usuario):
    activo = crear_usuario("activo@correo.com", rol="administrador")
    crear_usuario("suspendido@correo.com", rol="administrador", activo=False)
    r = client.patch(f"/api/usuarios/{activo.id}", json={"rol": "capturista"}, headers=encabezado_de(activo))
    assert r.status_code == 409  # el otro admin está suspendido: este es el único activo


def test_hu_01_4_usuario_inexistente_da_404(client, admin):
    r = client.patch("/api/usuarios/9999", json={"activo": False}, headers=encabezado_de(admin))
    assert r.status_code == 404


def test_hu_01_4_cambio_vacio_o_rol_invalido_da_422(client, admin, capturista):
    encabezado = encabezado_de(admin)
    assert client.patch(f"/api/usuarios/{capturista.id}", json={}, headers=encabezado).status_code == 422
    assert client.patch(f"/api/usuarios/{capturista.id}", json={"rol": "jefe"}, headers=encabezado).status_code == 422
