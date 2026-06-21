from flask import Flask, request, redirect, send_from_directory, session
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = "mouse_store_clave_secreta"


def conectar():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="benjamin1609",
        database="mousestore"
    )


@app.route("/")
def inicio():
    return send_from_directory(".", "index.html")


@app.route("/index.html")
def index():
    return send_from_directory(".", "index.html")


@app.route("/registro", methods=["POST"])
def registro():
    nombre = request.form["nombre"]
    correo = request.form["correo"]
    password = request.form["password"]

    conexion = conectar()
    cursor = conexion.cursor()

    try:
        cursor.execute(
            "INSERT INTO usuarios (nombre, correo, password) VALUES (%s, %s, %s)",
            (nombre, correo, password)
        )
        conexion.commit()
        return redirect("/login.html")

    except mysql.connector.IntegrityError:
        return "Ese correo ya está registrado. <br><br><a href='/registro.html'>Volver</a>"

    except Exception as error:
        return f"Error al registrar usuario: {error}"

    finally:
        cursor.close()
        conexion.close()


@app.route("/login", methods=["POST"])
def login():
    correo = request.form["correo"]
    password = request.form["password"]

    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM usuarios WHERE correo=%s AND password=%s",
        (correo, password)
    )

    usuario = cursor.fetchone()

    cursor.close()
    conexion.close()

    if usuario:
        session["usuario_id"] = usuario["id"]
        session["usuario_nombre"] = usuario["nombre"]
        session["usuario_correo"] = usuario["correo"]
        return redirect("/index.html")

    return "Correo o contraseña incorrectos. <br><br><a href='/login.html'>Volver</a>"


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/index.html")


@app.route("/usuario-activo")
def usuario_activo():
    if "usuario_nombre" in session:
        return {
            "logueado": True,
            "nombre": session["usuario_nombre"],
            "correo": session["usuario_correo"]
        }

    return {"logueado": False}


@app.route("/formulario-compra", methods=["POST"])
def formulario_compra():
    if "usuario_id" not in session:
        return redirect("/login.html")

    producto_id = request.form["producto_id"]
    color = request.form.get("color", "No aplica")

    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT * FROM productos WHERE id=%s", (producto_id,))
    producto = cursor.fetchone()

    cursor.close()
    conexion.close()

    if not producto:
        return "Producto no encontrado. <br><br><a href='/index.html'>Volver</a>"

    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Formulario de Compra | MouseStore</title>
        <link rel="icon" type="image/png" href="/logo.png">

        <style>
            *{{
                margin:0;
                padding:0;
                box-sizing:border-box;
            }}

            body{{
                font-family:Arial, sans-serif;
                background-image:url("/fondo.jpg");
                background-size:cover;
                background-position:center;
                background-attachment:fixed;
                color:white;
            }}

            .contenedor{{
                min-height:100vh;
                background:rgba(0,0,0,0.78);
                display:flex;
                justify-content:center;
                align-items:center;
                padding:40px;
            }}

            .checkout{{
                width:100%;
                max-width:1100px;
                display:grid;
                grid-template-columns:1fr 380px;
                gap:30px;
            }}

            .formulario, .resumen{{
                background:rgba(255,255,255,0.96);
                color:#111;
                padding:35px;
                border-radius:22px;
                box-shadow:0 0 30px black;
            }}

            h1{{
                color:#00bfff;
                margin-bottom:10px;
                font-size:38px;
            }}

            .subtitulo{{
                color:#555;
                margin-bottom:25px;
            }}

            .grid{{
                display:grid;
                grid-template-columns:1fr 1fr;
                gap:15px;
            }}

            label{{
                font-weight:bold;
                font-size:14px;
                margin-bottom:6px;
                display:block;
            }}

            input, select, textarea{{
                width:100%;
                padding:14px;
                border:1px solid #ccc;
                border-radius:10px;
                font-size:15px;
                margin-bottom:15px;
            }}

            textarea{{
                resize:none;
            }}

            .resumen h2{{
                color:#00bfff;
                margin-bottom:20px;
                text-align:center;
            }}

            .producto{{
                background:#111;
                color:white;
                padding:20px;
                border-radius:15px;
                text-align:center;
                margin-bottom:20px;
            }}

            .producto h3{{
                color:#00ff99;
                margin-bottom:10px;
            }}

            .fila{{
                display:flex;
                justify-content:space-between;
                margin:14px 0;
                font-size:17px;
            }}

            .total{{
                border-top:2px solid #ddd;
                padding-top:15px;
                margin-top:15px;
                font-size:25px;
                font-weight:bold;
                color:#00a85a;
            }}

            button{{
                width:100%;
                padding:15px;
                border:none;
                border-radius:12px;
                font-size:18px;
                cursor:pointer;
                color:white;
                font-weight:bold;
                transition:0.3s;
            }}

            button:hover{{
                transform:scale(1.03);
            }}

            .confirmar{{
                background:#00bfff;
                margin-top:15px;
            }}

            .confirmar:hover{{
                background:#009acd;
            }}

            .volver{{
                background:#28a745;
                margin-top:12px;
            }}

            .volver:hover{{
                background:#1f7d34;
            }}

            @media(max-width:900px){{
                .checkout{{
                    grid-template-columns:1fr;
                }}

                .grid{{
                    grid-template-columns:1fr;
                }}
            }}
        </style>
    </head>

    <body>

    <div class="contenedor">

        <div class="checkout">

            <div class="formulario">

                <h1>Datos de Entrega</h1>
                <p class="subtitulo">Completa tu información para confirmar el pedido.</p>

                <form action="/confirmar-compra" method="POST">

                    <input type="hidden" name="producto_id" value="{producto["id"]}">
                    <input type="hidden" name="color" value="{color}">

                    <div class="grid">
                        <div>
                            <label>Nombre completo</label>
                            <input type="text" name="nombre_cliente" required>
                        </div>

                        <div>
                            <label>DNI</label>
                            <input type="text" name="dni" maxlength="15" required>
                        </div>
                    </div>

                    <div class="grid">
                        <div>
                            <label>Correo electrónico</label>
                            <input type="email" name="correo_cliente" value="{session.get("usuario_correo", "")}" required>
                        </div>

                        <div>
                            <label>Teléfono</label>
                            <input type="tel" name="telefono" required>
                        </div>
                    </div>

                    <div class="grid">
                        <div>
                            <label>Departamento</label>
                            <input type="text" name="departamento" placeholder="Ej: Lima" required>
                        </div>

                        <div>
                            <label>Ciudad</label>
                            <input type="text" name="ciudad" placeholder="Ej: Lima" required>
                        </div>
                    </div>

                    <div class="grid">
                        <div>
                            <label>Distrito</label>
                            <input type="text" name="distrito" placeholder="Ej: Los Olivos" required>
                        </div>

                        <div>
                            <label>Cantidad</label>
                            <select name="cantidad" required>
                                <option value="1">1 unidad</option>
                                <option value="2">2 unidades</option>
                                <option value="3">3 unidades</option>
                                <option value="4">4 unidades</option>
                                <option value="5">5 unidades</option>
                            </select>
                        </div>
                    </div>

                    <label>Dirección exacta</label>
                    <input type="text" name="direccion" placeholder="Av. / Jr. / Calle / Referencia" required>

                    <label>Método de pago</label>
                    <select name="metodo_pago" required>
                        <option value="">Seleccione método de pago</option>
                        <option value="Yape">Yape</option>
                        <option value="Plin">Plin</option>
                        <option value="Tarjeta">Tarjeta</option>
                        <option value="Transferencia Bancaria">Transferencia Bancaria</option>
                    </select>

                    <label>Comentario adicional</label>
                    <textarea name="comentario" rows="3" placeholder="Referencia, horario de entrega, etc."></textarea>

                    <button class="confirmar" type="submit">
                        Confirmar Compra
                    </button>

                </form>

                <a href="/index.html">
                    <button class="volver">
                        Volver al Inicio
                    </button>
                </a>

            </div>

            <div class="resumen">

                <h2>Resumen del Pedido</h2>

                <div class="producto">
                    <h3>{producto["nombre"]}</h3>
                    <p>{producto["descripcion"]}</p>
                </div>

                <div class="fila">
                    <span>Color:</span>
                    <strong>{color}</strong>
                </div>

                <div class="fila">
                    <span>Precio:</span>
                    <strong>S/ {producto["precio"]}</strong>
                </div>

                <div class="fila">
                    <span>Envío:</span>
                    <strong>Gratis</strong>
                </div>

                <div class="fila">
                    <span>Estado:</span>
                    <strong>Confirmado</strong>
                </div>

                <div class="fila total">
                    <span>Total:</span>
                    <span>S/ {producto["precio"]}</span>
                </div>

            </div>

        </div>

    </div>

    </body>
    </html>
    """

    return html


@app.route("/confirmar-compra", methods=["POST"])
def confirmar_compra():
    if "usuario_id" not in session:
        return redirect("/login.html")

    usuario_id = session["usuario_id"]
    producto_id = request.form["producto_id"]
    cantidad = int(request.form["cantidad"])
    color = request.form.get("color", "No aplica")

    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute("SELECT precio FROM productos WHERE id=%s", (producto_id,))
        producto = cursor.fetchone()

        if not producto:
            return "Producto no encontrado."

        precio = float(producto["precio"])
        total = precio * cantidad

        nombre_cliente = request.form["nombre_cliente"]
        dni = request.form["dni"]
        correo_cliente = request.form["correo_cliente"]
        telefono = request.form["telefono"]
        departamento = request.form["departamento"]
        ciudad = request.form["ciudad"]
        distrito = request.form["distrito"]
        direccion = request.form["direccion"]
        metodo_pago = request.form["metodo_pago"]

        cursor.execute(
            """
            INSERT INTO compras
            (usuario_id, total, nombre_cliente, telefono, direccion, metodo_pago,
             dni, correo_cliente, departamento, ciudad, distrito, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Confirmado')
            """,
            (
                usuario_id, total, nombre_cliente, telefono, direccion, metodo_pago,
                dni, correo_cliente, departamento, ciudad, distrito
            )
        )

        conexion.commit()

        compra_id = cursor.lastrowid
        numero_orden = f"MS-{compra_id:06d}"

        cursor.execute(
            "UPDATE compras SET numero_orden=%s WHERE id=%s",
            (numero_orden, compra_id)
        )

        cursor.execute(
            """
            INSERT INTO detalle_compras
            (compra_id, producto_id, cantidad, subtotal, color)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (compra_id, producto_id, cantidad, total, color)
        )

        conexion.commit()

        return redirect("/mis-compras")

    except Exception as error:
        return f"Error al confirmar compra: {error}"

    finally:
        cursor.close()
        conexion.close()


@app.route("/mis-compras")
def mis_compras():
    if "usuario_id" not in session:
        return redirect("/login.html")

    usuario_id = session["usuario_id"]

    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT 
            c.id AS compra_id,
            c.numero_orden,
            c.fecha_compra,
            c.total,
            c.nombre_cliente,
            c.dni,
            c.correo_cliente,
            c.telefono,
            c.departamento,
            c.ciudad,
            c.distrito,
            c.direccion,
            c.metodo_pago,
            c.estado,
            p.nombre AS producto,
            p.precio AS precio_unitario,
            d.cantidad,
            d.subtotal,
            d.color
        FROM compras c
        INNER JOIN detalle_compras d ON c.id = d.compra_id
        INNER JOIN productos p ON d.producto_id = p.id
        WHERE c.usuario_id = %s
        ORDER BY c.fecha_compra DESC
        """,
        (usuario_id,)
    )

    compras = cursor.fetchall()

    cursor.close()
    conexion.close()

    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Mis Compras | MouseStore</title>
        <link rel="icon" type="image/png" href="/logo.png">

        <style>
            *{
                margin:0;
                padding:0;
                box-sizing:border-box;
            }

            body{
                font-family:Arial, sans-serif;
                background-image:url("/fondo.jpg");
                background-size:cover;
                background-position:center;
                background-attachment:fixed;
                color:white;
            }

            nav{
                background:rgba(0,0,0,0.92);
                display:flex;
                justify-content:space-between;
                align-items:center;
                padding:18px 50px;
                box-shadow:0 0 18px black;
            }

            nav h1{
                color:#00bfff;
                font-size:32px;
            }

            nav a{
                color:white;
                text-decoration:none;
                margin-left:20px;
                font-size:17px;
                font-weight:bold;
            }

            nav a:hover{
                color:#00bfff;
            }

            .contenedor{
                min-height:100vh;
                background:rgba(0,0,0,0.78);
                padding:50px 20px;
            }

            .titulo{
                text-align:center;
                margin-bottom:35px;
            }

            .titulo h2{
                color:#00bfff;
                font-size:48px;
                margin-bottom:10px;
            }

            .titulo p{
                color:#ddd;
                font-size:18px;
            }

            .compras-grid{
                max-width:1150px;
                margin:auto;
                display:grid;
                grid-template-columns:repeat(auto-fit,minmax(330px,1fr));
                gap:28px;
            }

            .boleta{
                background:rgba(255,255,255,0.96);
                color:#111;
                border-radius:22px;
                overflow:hidden;
                box-shadow:0 0 25px rgba(0,0,0,0.75);
                transition:0.3s;
            }

            .boleta:hover{
                transform:translateY(-6px);
                box-shadow:0 0 35px rgba(0,191,255,0.55);
            }

            .boleta-header{
                background:#00bfff;
                color:white;
                padding:20px;
                text-align:center;
            }

            .boleta-header h3{
                font-size:24px;
                margin-bottom:6px;
            }

            .orden{
                font-size:15px;
                background:rgba(0,0,0,0.18);
                display:inline-block;
                padding:6px 12px;
                border-radius:20px;
            }

            .boleta-body{
                padding:25px;
            }

            .producto{
                background:#111;
                color:white;
                padding:18px;
                border-radius:15px;
                text-align:center;
                margin-bottom:18px;
            }

            .producto h4{
                color:#00ff99;
                font-size:22px;
                margin-bottom:8px;
            }

            .estado{
                display:inline-block;
                background:#28a745;
                color:white;
                padding:6px 12px;
                border-radius:20px;
                font-size:14px;
                font-weight:bold;
                margin-top:8px;
            }

            .dato{
                display:flex;
                justify-content:space-between;
                gap:15px;
                padding:10px 0;
                border-bottom:1px solid #ddd;
                font-size:15px;
            }

            .dato span{
                color:#555;
                font-weight:bold;
            }

            .dato strong{
                text-align:right;
            }

            .total{
                margin-top:18px;
                background:#111;
                color:white;
                padding:18px;
                border-radius:15px;
                display:flex;
                justify-content:space-between;
                align-items:center;
                font-size:24px;
                font-weight:bold;
            }

            .total strong{
                color:#00ff99;
            }

            .cliente{
                margin-top:18px;
                background:#f3f3f3;
                padding:15px;
                border-radius:15px;
            }

            .cliente h4{
                color:#00bfff;
                margin-bottom:10px;
                font-size:18px;
            }

            .vacio{
                max-width:700px;
                margin:70px auto;
                background:rgba(255,255,255,0.95);
                color:#111;
                text-align:center;
                padding:45px;
                border-radius:22px;
                box-shadow:0 0 25px black;
            }

            .vacio h3{
                font-size:32px;
                color:#00bfff;
                margin-bottom:15px;
            }

            .vacio a{
                display:inline-block;
                margin-top:20px;
                background:#00bfff;
                color:white;
                padding:14px 25px;
                border-radius:10px;
                text-decoration:none;
                font-weight:bold;
            }

            .vacio a:hover{
                background:#009acd;
            }

            footer{
                background:rgba(0,0,0,0.95);
                text-align:center;
                padding:25px;
                color:white;
            }

            @media(max-width:600px){
                nav{
                    flex-direction:column;
                    gap:12px;
                }

                .titulo h2{
                    font-size:36px;
                }

                .dato{
                    flex-direction:column;
                }

                .dato strong{
                    text-align:left;
                }
            }
        </style>
    </head>

    <body>

    <nav>
        <h1>🖱 MouseStore</h1>
        <div>
            <a href="/index.html">Inicio</a>
            <a href="/logout">Cerrar Sesión</a>
        </div>
    </nav>

    <div class="contenedor">

        <div class="titulo">
            <h2>📦 Mis Compras</h2>
            <p>Historial de pedidos realizados en MouseStore</p>
        </div>
    """

    if len(compras) == 0:
        html += """
        <div class="vacio">
            <h3>No tienes compras registradas</h3>
            <p>Cuando compres un producto, tu pedido aparecerá aquí.</p>
            <a href="/index.html">Explorar productos</a>
        </div>
        """
    else:
        html += """
        <div class="compras-grid">
        """

        for compra in compras:
            color = compra["color"] if compra["color"] else "No aplica"
            orden = compra["numero_orden"] if compra["numero_orden"] else f"MS-{compra['compra_id']:06d}"

            html += f"""
            <div class="boleta">

                <div class="boleta-header">
                    <h3>Comprobante de Compra</h3>
                    <div class="orden">{orden}</div>
                </div>

                <div class="boleta-body">

                    <div class="producto">
                        <h4>{compra['producto']}</h4>
                        <p>Color: {color}</p>
                        <span class="estado">{compra['estado']}</span>
                    </div>

                    <div class="dato">
                        <span>Cantidad</span>
                        <strong>{compra['cantidad']}</strong>
                    </div>

                    <div class="dato">
                        <span>Precio unitario</span>
                        <strong>S/ {compra['precio_unitario']}</strong>
                    </div>

                    <div class="dato">
                        <span>Método de pago</span>
                        <strong>{compra['metodo_pago']}</strong>
                    </div>

                    <div class="dato">
                        <span>Fecha</span>
                        <strong>{compra['fecha_compra']}</strong>
                    </div>

                    <div class="cliente">
                        <h4>Datos de entrega</h4>

                        <div class="dato">
                            <span>Cliente</span>
                            <strong>{compra['nombre_cliente']}</strong>
                        </div>

                        <div class="dato">
                            <span>DNI</span>
                            <strong>{compra['dni']}</strong>
                        </div>

                        <div class="dato">
                            <span>Teléfono</span>
                            <strong>{compra['telefono']}</strong>
                        </div>

                        <div class="dato">
                            <span>Correo</span>
                            <strong>{compra['correo_cliente']}</strong>
                        </div>

                        <div class="dato">
                            <span>Ubicación</span>
                            <strong>{compra['departamento']} - {compra['ciudad']} - {compra['distrito']}</strong>
                        </div>

                        <div class="dato">
                            <span>Dirección</span>
                            <strong>{compra['direccion']}</strong>
                        </div>
                    </div>

                   <div class="total">
    <span>Total</span>
    <strong>S/ {compra['total']}</strong>
</div>

<a href="/boleta/{compra['compra_id']}" style="text-decoration:none;">
    <button style="
        width:100%;
        margin-top:15px;
        padding:14px;
        border:none;
        border-radius:12px;
        background:#00bfff;
        color:white;
        font-size:17px;
        font-weight:bold;
        cursor:pointer;
    ">
        📄 Ver Boleta Profesional
    </button>
</a>

                </div>

            </div>
            """

        html += """
        </div>
        """

    html += """
    </div>

    <footer>
        <p>© 2026 MouseStore - Historial de compras</p>
    </footer>

    </body>
    </html>
    """

    return html

@app.route("/boleta/<int:compra_id>")
def boleta(compra_id):
    if "usuario_id" not in session:
        return redirect("/login.html")

    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT 
            c.id AS compra_id,
            c.numero_orden,
            c.fecha_compra,
            c.total,
            c.nombre_cliente,
            c.dni,
            c.correo_cliente,
            c.telefono,
            c.departamento,
            c.ciudad,
            c.distrito,
            c.direccion,
            c.metodo_pago,
            c.estado,
            p.nombre AS producto,
            p.precio AS precio_unitario,
            d.cantidad,
            d.subtotal,
            d.color
        FROM compras c
        INNER JOIN detalle_compras d ON c.id = d.compra_id
        INNER JOIN productos p ON d.producto_id = p.id
        WHERE c.id = %s AND c.usuario_id = %s
        """,
        (compra_id, session["usuario_id"])
    )

    compra = cursor.fetchone()

    cursor.close()
    conexion.close()

    if not compra:
        return "Boleta no encontrada. <br><br><a href='/mis-compras'>Volver</a>"

    color = compra["color"] if compra["color"] else "No aplica"
    orden = compra["numero_orden"] if compra["numero_orden"] else f"MS-{compra['compra_id']:06d}"
    producto_nombre = compra["producto"]

    if "RGB" in producto_nombre:
        if color == "Negro":
            imagen_producto = "/rgb-negro.jpg"
        elif color == "Blanco":
            imagen_producto = "/rgb-blanco.jpg"
        else:
            imagen_producto = "/rgb.jpg"
    elif "Inalambrico" in producto_nombre or "Inalámbrico" in producto_nombre:
        imagen_producto = "/inalambrico.jpg"
    elif "Pro X" in producto_nombre:
        imagen_producto = "/prox.jpg"
    else:
        imagen_producto = "/logo.png"

    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Boleta {orden} | MouseStore</title>
        <link rel="icon" type="image/png" href="/logo.png">

        <style>
            *{{
                margin:0;
                padding:0;
                box-sizing:border-box;
            }}

            body{{
                font-family:Arial, sans-serif;
                background:linear-gradient(135deg,#0b0b0b,#1b1b1b);
                padding:35px;
                color:#111;
            }}

            .boleta{{
                max-width:850px;
                margin:auto;
                background:white;
                border-radius:22px;
                overflow:hidden;
                box-shadow:0 0 35px rgba(0,0,0,.85);
            }}

            .header{{
                background:#101010;
                color:white;
                text-align:center;
                padding:35px 25px;
                border-bottom:5px solid #00bfff;
            }}

            .header img{{
                width:90px;
                margin-bottom:10px;
            }}

            .header h1{{
                color:#00bfff;
                font-size:40px;
                margin-bottom:8px;
            }}

            .orden{{
                display:inline-block;
                background:#00bfff;
                color:white;
                padding:8px 16px;
                border-radius:20px;
                font-size:18px;
                font-weight:bold;
                margin-top:10px;
            }}

            .estado-confirmado{{
                background:#28a745;
                color:white;
                padding:12px;
                border-radius:10px;
                margin:15px auto;
                width:260px;
                font-weight:bold;
                text-align:center;
                box-shadow:0 0 12px rgba(40,167,69,.6);
            }}

            .contenido{{
                padding:35px 40px;
            }}

            .seccion{{
                margin-bottom:28px;
                background:#f7f7f7;
                padding:22px;
                border-radius:16px;
                border-left:5px solid #00bfff;
            }}

            .seccion h2{{
                color:#00bfff;
                margin-bottom:14px;
                font-size:24px;
            }}

            .fila{{
                display:flex;
                justify-content:space-between;
                gap:20px;
                border-bottom:1px solid #ddd;
                padding:11px 0;
                font-size:16px;
            }}

            .fila:last-child{{
                border-bottom:none;
            }}

            .fila span{{
                font-weight:bold;
                color:#555;
            }}

            .fila strong{{
                text-align:right;
                color:#111;
            }}

            .imagen-producto{{
                text-align:center;
                margin:20px 0;
            }}

            .imagen-producto img{{
                width:190px;
                height:190px;
                object-fit:contain;
                border-radius:15px;
                background:white;
                padding:10px;
                box-shadow:0 0 15px rgba(0,0,0,.25);
            }}

            .producto-tabla{{
                width:100%;
                border-collapse:collapse;
                margin-top:10px;
                border-radius:14px;
                overflow:hidden;
            }}

            .producto-tabla th{{
                background:#111;
                color:white;
                padding:14px;
                font-size:15px;
            }}

            .producto-tabla td{{
                padding:14px;
                text-align:center;
                border-bottom:1px solid #ddd;
                background:white;
            }}

            .total{{
                margin-top:25px;
                background:#111;
                color:white;
                padding:22px;
                border-radius:16px;
                display:flex;
                justify-content:space-between;
                align-items:center;
                font-size:30px;
                font-weight:bold;
            }}

            .total strong{{
                color:#00ff99;
            }}

            .nota{{
                margin-top:25px;
                text-align:center;
                color:#555;
                font-size:14px;
            }}

            .botones{{
                max-width:850px;
                margin:25px auto;
                display:flex;
                gap:15px;
                justify-content:center;
                flex-wrap:wrap;
            }}

            button{{
                border:none;
                padding:14px 25px;
                border-radius:10px;
                color:white;
                font-size:17px;
                cursor:pointer;
                font-weight:bold;
                transition:.3s;
            }}

            button:hover{{
                transform:scale(1.05);
            }}

            .imprimir{{
                background:#00bfff;
            }}

            .volver{{
                background:#28a745;
            }}

            @media print{{
                body{{
                    background:white;
                    padding:0;
                }}

                .botones{{
                    display:none;
                }}

                .boleta{{
                    box-shadow:none;
                    border-radius:0;
                    max-width:100%;
                }}

                .header,
                .total{{
                    -webkit-print-color-adjust:exact;
                    print-color-adjust:exact;
                }}
            }}
        </style>
    </head>

    <body>

        <div class="boleta">

            <div class="header">
                <img src="/logo.png" alt="Logo MouseStore">

                <h1>🖱 MouseStore</h1>

                <div class="estado-confirmado">
                    ✔ PEDIDO CONFIRMADO
                </div>

                <p>Boleta de Compra</p>

                <p class="orden">{orden}</p>
            </div>

            <div class="contenido">

                <div class="seccion">
                    <h2>Datos del Cliente</h2>
                    <div class="fila"><span>Cliente:</span><strong>{compra['nombre_cliente']}</strong></div>
                    <div class="fila"><span>DNI:</span><strong>{compra['dni']}</strong></div>
                    <div class="fila"><span>Correo:</span><strong>{compra['correo_cliente']}</strong></div>
                    <div class="fila"><span>Teléfono:</span><strong>{compra['telefono']}</strong></div>
                </div>

                <div class="seccion">
                    <h2>Datos de Entrega</h2>
                    <div class="fila"><span>Departamento:</span><strong>{compra['departamento']}</strong></div>
                    <div class="fila"><span>Ciudad:</span><strong>{compra['ciudad']}</strong></div>
                    <div class="fila"><span>Distrito:</span><strong>{compra['distrito']}</strong></div>
                    <div class="fila"><span>Dirección:</span><strong>{compra['direccion']}</strong></div>
                </div>

                <div class="seccion">
                    <h2>Detalle del Producto</h2>

                    <div class="imagen-producto">
                        <img src="{imagen_producto}" alt="{compra['producto']}">
                    </div>

                    <table class="producto-tabla">
                        <tr>
                            <th>Producto</th>
                            <th>Color</th>
                            <th>Cantidad</th>
                            <th>Precio</th>
                            <th>Subtotal</th>
                        </tr>

                        <tr>
                            <td>{compra['producto']}</td>
                            <td>{color}</td>
                            <td>{compra['cantidad']}</td>
                            <td>S/ {compra['precio_unitario']}</td>
                            <td>S/ {compra['subtotal']}</td>
                        </tr>
                    </table>

                    <div class="fila"><span>Método de pago:</span><strong>{compra['metodo_pago']}</strong></div>
                    <div class="fila"><span>Estado:</span><strong>{compra['estado']}</strong></div>
                    <div class="fila"><span>Fecha:</span><strong>{compra['fecha_compra']}</strong></div>
                </div>

                <div class="total">
                    <span>Total pagado</span>
                    <strong>S/ {compra['total']}</strong>
                </div>

                <p class="nota">
                    Gracias por comprar en MouseStore. Esta boleta puede imprimirse o guardarse como PDF desde el navegador.
                </p>

            </div>

        </div>

        <div class="botones">
            <button class="imprimir" onclick="window.print()">🖨 Imprimir / Guardar PDF</button>

            <a href="/mis-compras">
                <button class="volver">Volver</button>
            </a>
        </div>

    </body>
    </html>
    """

@app.route("/admin-usuarios")
def admin_usuarios():
    if "usuario_correo" not in session:
        return "Acceso denegado. Primero inicia sesión. <br><br><a href='/login.html'>Ir al Login</a>"

    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM usuarios")
    total_usuarios = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM compras")
    total_compras = cursor.fetchone()["total"]

    cursor.execute("SELECT IFNULL(SUM(total), 0) AS ventas FROM compras")
    ventas_totales = cursor.fetchone()["ventas"]

    cursor.execute("SELECT IFNULL(SUM(total), 0) AS ventas_hoy FROM compras WHERE DATE(fecha_compra) = CURDATE()")
    ventas_hoy = cursor.fetchone()["ventas_hoy"]

    cursor.execute("""
        SELECT IFNULL(SUM(total), 0) AS ventas_mes
        FROM compras
        WHERE MONTH(fecha_compra)=MONTH(CURDATE())
        AND YEAR(fecha_compra)=YEAR(CURDATE())
    """)
    ventas_mes = cursor.fetchone()["ventas_mes"]

    cursor.execute("SELECT IFNULL(AVG(total), 0) AS ticket FROM compras")
    ticket_promedio = cursor.fetchone()["ticket"]

    cursor.execute("""
        SELECT p.nombre AS producto, SUM(d.cantidad) AS cantidad
        FROM detalle_compras d
        INNER JOIN productos p ON d.producto_id = p.id
        GROUP BY p.nombre
        ORDER BY cantidad DESC
        LIMIT 1
    """)
    producto_mas_vendido = cursor.fetchone()

    cursor.execute("""
        SELECT 
            p.nombre AS producto,
            SUM(d.cantidad) AS cantidad,
            IFNULL(SUM(d.subtotal),0) AS total_vendido
        FROM detalle_compras d
        INNER JOIN productos p ON d.producto_id = p.id
        GROUP BY p.nombre
        ORDER BY cantidad DESC
    """)
    ventas_por_producto = cursor.fetchall()

    cursor.execute("""
        SELECT estado, COUNT(*) AS cantidad
        FROM compras
        GROUP BY estado
    """)
    pedidos_por_estado = cursor.fetchall()

    cursor.execute("""
        SELECT 
            nombre_cliente,
            correo_cliente,
            COUNT(*) AS total_pedidos,
            IFNULL(SUM(total),0) AS total_gastado
        FROM compras
        WHERE nombre_cliente IS NOT NULL
        GROUP BY nombre_cliente, correo_cliente
        ORDER BY total_pedidos DESC
        LIMIT 1
    """)
    cliente_top = cursor.fetchone()

    cursor.execute("""
        SELECT p.nombre AS producto, IFNULL(SUM(d.subtotal),0) AS ingresos
        FROM detalle_compras d
        INNER JOIN productos p ON d.producto_id = p.id
        GROUP BY p.nombre
        ORDER BY ingresos DESC
        LIMIT 1
    """)
    producto_mas_rentable = cursor.fetchone()

    cursor.execute("""
        SELECT p.nombre AS producto, SUM(d.cantidad) AS cantidad
        FROM detalle_compras d
        INNER JOIN productos p ON d.producto_id = p.id
        GROUP BY p.nombre
        ORDER BY cantidad DESC
        LIMIT 5
    """)
    top_productos = cursor.fetchall()

    cursor.execute("""
        SELECT metodo_pago, COUNT(*) AS cantidad, IFNULL(SUM(total),0) AS total
        FROM compras
        GROUP BY metodo_pago
        ORDER BY cantidad DESC
    """)
    metodos_pago = cursor.fetchall()

    cursor.execute("""
        SELECT 
            c.id,
            c.numero_orden,
            c.nombre_cliente,
            c.correo_cliente,
            c.metodo_pago,
            c.estado,
            c.total,
            c.fecha_compra,
            p.nombre AS producto,
            d.cantidad,
            d.color
        FROM compras c
        INNER JOIN detalle_compras d ON c.id = d.compra_id
        INNER JOIN productos p ON d.producto_id = p.id
        ORDER BY c.fecha_compra DESC
        LIMIT 10
    """)
    ultimas_compras = cursor.fetchall()

    cursor.execute("""
        SELECT id, nombre, correo, fecha_registro
        FROM usuarios
        ORDER BY fecha_registro DESC
        LIMIT 10
    """)
    usuarios = cursor.fetchall()

    cursor.close()
    conexion.close()

    producto_top = producto_mas_vendido["producto"] if producto_mas_vendido else "Sin ventas"
    producto_top_cantidad = producto_mas_vendido["cantidad"] if producto_mas_vendido else 0
    producto_rentable = producto_mas_rentable["producto"] if producto_mas_rentable else "Sin datos"
    producto_rentable_ingresos = producto_mas_rentable["ingresos"] if producto_mas_rentable else 0

    max_venta = 1
    if ventas_por_producto:
        max_venta = max([float(p["total_vendido"]) for p in ventas_por_producto])

    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Dashboard Admin | MouseStore</title>
        <link rel="icon" type="image/png" href="/logo.png">

        <style>
            *{{margin:0;padding:0;box-sizing:border-box;}}

            body{{
                font-family:Arial, sans-serif;
                background:#07111f;
                color:white;
            }}

            .dashboard{{
                display:grid;
                grid-template-columns:260px 1fr;
                min-height:100vh;
            }}

            .sidebar{{
                background:linear-gradient(180deg,#101b33,#07111f);
                padding:25px;
                border-right:1px solid rgba(255,255,255,.08);
            }}

            .logo{{
                font-size:32px;
                font-weight:bold;
                margin-bottom:35px;
            }}

            .logo span{{color:#8b5cf6;}}

            .perfil{{
                background:rgba(255,255,255,.08);
                padding:18px;
                border-radius:18px;
                margin-bottom:30px;
            }}

            .perfil h3{{font-size:18px;}}
            .perfil p{{color:#aaa;font-size:14px;margin-top:5px;}}
            .online{{color:#00ff99;font-size:13px;margin-top:8px;}}

            .menu a{{
                display:block;
                color:white;
                text-decoration:none;
                padding:15px;
                border-radius:14px;
                margin-bottom:10px;
                font-weight:bold;
            }}

            .menu a:hover,.activo{{
                background:linear-gradient(90deg,#6d28d9,#2563eb);
            }}

            .main{{
                padding:28px;
                background:radial-gradient(circle at top,#13233f,#07111f);
            }}

            .topbar{{
                display:flex;
                justify-content:space-between;
                align-items:center;
                margin-bottom:28px;
            }}

            .topbar h1{{font-size:36px;}}

            .exportar{{
                background:#7c3aed;
                color:white;
                border:none;
                padding:13px 20px;
                border-radius:12px;
                font-weight:bold;
                cursor:pointer;
            }}

            .cards{{
                display:grid;
                grid-template-columns:repeat(auto-fit,minmax(210px,1fr));
                gap:18px;
                margin-bottom:22px;
            }}

            .card{{
                background:rgba(255,255,255,.07);
                border:1px solid rgba(255,255,255,.08);
                padding:22px;
                border-radius:20px;
                box-shadow:0 0 18px rgba(0,0,0,.35);
            }}

            .card small{{color:#aaa;font-weight:bold;}}
            .card h2{{margin-top:12px;font-size:30px;}}
            .verde{{color:#00ff99;}}
            .azul{{color:#38bdf8;}}
            .morado{{color:#a78bfa;}}
            .naranja{{color:#f59e0b;}}

            .grid{{
                display:grid;
                grid-template-columns:1.4fr 1fr 1fr;
                gap:18px;
                margin-bottom:20px;
            }}

            .panel{{
                background:rgba(255,255,255,.07);
                border:1px solid rgba(255,255,255,.08);
                border-radius:20px;
                padding:22px;
                box-shadow:0 0 18px rgba(0,0,0,.35);
                overflow-x:auto;
            }}

            .panel h3{{
                margin-bottom:18px;
                font-size:20px;
            }}

            .grafico{{
                display:flex;
                align-items:end;
                gap:18px;
                height:245px;
                padding:20px 10px 35px 10px;
            }}

            .barra{{
                flex:1;
                background:linear-gradient(180deg,#8b5cf6,#2563eb);
                border-radius:10px 10px 0 0;
                min-height:25px;
                position:relative;
            }}

            .barra strong{{
                position:absolute;
                top:-25px;
                left:50%;
                transform:translateX(-50%);
                font-size:12px;
                color:#fff;
            }}

            .barra span{{
                position:absolute;
                bottom:-30px;
                left:50%;
                transform:translateX(-50%);
                font-size:12px;
                color:#ccc;
                white-space:nowrap;
            }}

            .lista div{{
                display:flex;
                justify-content:space-between;
                padding:12px 0;
                border-bottom:1px solid rgba(255,255,255,.08);
            }}

            table{{
                width:100%;
                border-collapse:collapse;
                color:white;
            }}

            th,td{{
                padding:13px;
                text-align:left;
                border-bottom:1px solid rgba(255,255,255,.08);
                font-size:14px;
            }}

            th{{color:#38bdf8;}}

            .estado{{
                padding:7px 11px;
                border-radius:20px;
                font-size:13px;
                font-weight:bold;
                border:none;
            }}

            .Confirmado{{background:#16a34a;color:white;}}
            .Preparando{{background:#ca8a04;color:white;}}
            .Enviado{{background:#2563eb;color:white;}}
            .Entregado{{background:#7c3aed;color:white;}}

            .btn{{
                display:inline-block;
                text-decoration:none;
                color:white;
                padding:8px 12px;
                border-radius:9px;
                font-size:13px;
                font-weight:bold;
            }}

            .boleta{{background:#2563eb;}}
            .eliminar{{background:#dc3545;}}
            .tablas{{
                display:grid;
                grid-template-columns:2fr 1fr;
                gap:18px;
                margin-bottom:20px;
            }}

            .resumen{{
                display:grid;
                grid-template-columns:1fr 1fr;
                gap:18px;
                margin-bottom:20px;
            }}

            @media(max-width:1100px){{
                .dashboard{{grid-template-columns:1fr;}}
                .sidebar{{display:none;}}
                .grid,.tablas,.resumen{{grid-template-columns:1fr;}}
            }}
        </style>
    </head>

    <body>

    <div class="dashboard">

        <aside class="sidebar">
            <div class="logo">Mouse<span>Store</span></div>

            <div class="perfil">
                <h3>Administrador</h3>
                <p>{session.get("usuario_correo", "admin@mousestore.com")}</p>
                <div class="online">● En línea</div>
            </div>

            <div class="menu">
                <a class="activo" href="/admin-usuarios">📊 Dashboard</a>
                <a href="/index.html">🏠 Inicio</a>
                <a href="/mis-compras">📦 Mis Compras</a>
                <a href="/logout">🚪 Cerrar sesión</a>
            </div>
        </aside>

        <main class="main">

            <div class="topbar">
                <h1>Dashboard</h1>
                <button class="exportar" onclick="window.print()">⬇ Exportar</button>
            </div>

            <section class="cards">
                <div class="card"><small>VENTAS TOTALES</small><h2 class="morado">S/ {round(float(ventas_totales),2)}</h2><p class="verde">↑ Datos de MySQL</p></div>
                <div class="card"><small>VENTAS DE HOY</small><h2 class="azul">S/ {round(float(ventas_hoy),2)}</h2><p class="verde">↑ Día actual</p></div>
                <div class="card"><small>VENTAS DEL MES</small><h2 class="verde">S/ {round(float(ventas_mes),2)}</h2><p class="verde">↑ Mes actual</p></div>
                <div class="card"><small>PEDIDOS TOTALES</small><h2 class="naranja">{total_compras}</h2><p class="verde">Pedidos registrados</p></div>
                <div class="card"><small>CLIENTES REGISTRADOS</small><h2 class="azul">{total_usuarios}</h2><p class="verde">Usuarios activos</p></div>
                <div class="card"><small>TICKET PROMEDIO</small><h2 class="morado">S/ {round(float(ticket_promedio),2)}</h2><p class="verde">Promedio por compra</p></div>
            </section>

            <section class="grid">

                <div class="panel">
                    <h3>📈 Ventas por producto</h3>
                    <div class="grafico">
    """

    for producto in ventas_por_producto:
        altura = max(int((float(producto["total_vendido"]) / max_venta) * 200), 25)
        nombre_corto = producto["producto"][:10]
        html += f"""
                        <div class="barra" style="height:{altura}px">
                            <strong>S/ {round(float(producto['total_vendido']),2)}</strong>
                            <span>{nombre_corto}</span>
                        </div>
        """

    if not ventas_por_producto:
        html += "<p>No hay ventas registradas.</p>"

    html += """
                    </div>
                </div>

                <div class="panel">
                    <h3>📦 Pedidos por estado</h3>
                    <div class="lista">
    """

    for estado in pedidos_por_estado:
        html += f"""
                        <div><span>{estado['estado']}</span><strong>{estado['cantidad']}</strong></div>
        """

    if not pedidos_por_estado:
        html += "<p>No hay pedidos registrados.</p>"

    html += """
                    </div>
                </div>

                <div class="panel">
                    <h3>🏆 Top productos</h3>
                    <div class="lista">
    """

    for i, producto in enumerate(top_productos, start=1):
        html += f"""
                        <div><span>{i}. {producto['producto']}</span><strong>{producto['cantidad']} uds</strong></div>
        """

    if not top_productos:
        html += "<p>No hay productos vendidos.</p>"

    html += f"""
                    </div>
                </div>

            </section>

            <section class="resumen">
                <div class="panel">
                    <h3>🔥 Producto más vendido</h3>
                    <div class="lista">
                        <div><span>Producto</span><strong>{producto_top}</strong></div>
                        <div><span>Unidades</span><strong>{producto_top_cantidad}</strong></div>
                    </div>
                </div>

                <div class="panel">
                    <h3>💰 Producto más rentable</h3>
                    <div class="lista">
                        <div><span>Producto</span><strong>{producto_rentable}</strong></div>
                        <div><span>Ingresos</span><strong>S/ {round(float(producto_rentable_ingresos),2)}</strong></div>
                    </div>
                </div>
            </section>

            <section class="grid">
                <div class="panel">
                    <h3>💳 Métodos de pago</h3>
                    <div class="lista">
    """

    for metodo in metodos_pago:
        html += f"""
                        <div><span>{metodo['metodo_pago']}</span><strong>{metodo['cantidad']} pagos | S/ {round(float(metodo['total']),2)}</strong></div>
        """

    if not metodos_pago:
        html += "<p>No hay métodos de pago registrados.</p>"

    html += """
                    </div>
                </div>

                <div class="panel">
                    <h3>👑 Cliente top</h3>
                    <div class="lista">
    """

    if cliente_top:
        html += f"""
                        <div><span>Cliente</span><strong>{cliente_top['nombre_cliente']}</strong></div>
                        <div><span>Pedidos</span><strong>{cliente_top['total_pedidos']}</strong></div>
                        <div><span>Total gastado</span><strong>S/ {round(float(cliente_top['total_gastado']),2)}</strong></div>
        """
    else:
        html += "<p>No hay cliente top registrado.</p>"

    html += """
                    </div>
                </div>

                <div class="panel">
                    <h3>📌 Resumen rápido</h3>
                    <div class="lista">
    """

    html += f"""
                        <div><span>Usuarios</span><strong>{total_usuarios}</strong></div>
                        <div><span>Pedidos</span><strong>{total_compras}</strong></div>
                        <div><span>Ventas</span><strong>S/ {round(float(ventas_totales),2)}</strong></div>
                    </div>
                </div>
            </section>

            <section class="tablas">

                <div class="panel">
                    <h3>🛒 Últimas compras</h3>
                    <table>
                        <tr>
                            <th>Orden</th>
                            <th>Cliente</th>
                            <th>Producto</th>
                            <th>Total</th>
                            <th>Estado</th>
                            <th>Fecha</th>
                            <th>Boleta</th>
                        </tr>
    """

    for compra in ultimas_compras:
        orden = compra["numero_orden"] if compra["numero_orden"] else "Sin orden"
        estado_actual = compra["estado"] if compra["estado"] else "Confirmado"

        html += f"""
                        <tr>
                            <td>{orden}</td>
                            <td>{compra['nombre_cliente']}</td>
                            <td>{compra['producto']}</td>
                            <td>S/ {compra['total']}</td>
                            <td>
                                <form action="/cambiar-estado" method="POST">
                                    <input type="hidden" name="compra_id" value="{compra['id']}">
                                    <select class="estado {estado_actual}" name="estado" onchange="this.form.submit()">
                                        <option value="Confirmado" {"selected" if estado_actual == "Confirmado" else ""}>Confirmado</option>
                                        <option value="Preparando" {"selected" if estado_actual == "Preparando" else ""}>Preparando</option>
                                        <option value="Enviado" {"selected" if estado_actual == "Enviado" else ""}>Enviado</option>
                                        <option value="Entregado" {"selected" if estado_actual == "Entregado" else ""}>Entregado</option>
                                    </select>
                                </form>
                            </td>
                            <td>{compra['fecha_compra']}</td>
                            <td><a class="btn boleta" href="/boleta/{compra['id']}">Ver</a></td>
                        </tr>
        """

    html += """
                    </table>
                </div>

                <div class="panel">
                    <h3>👤 Usuarios recientes</h3>
                    <table>
                        <tr>
                            <th>Nombre</th>
                            <th>Correo</th>
                        </tr>
    """

    for usuario in usuarios:
        html += f"""
                        <tr>
                            <td>{usuario['nombre']}</td>
                            <td>{usuario['correo']}</td>
                        </tr>
        """

    html += """
                    </table>
                </div>

            </section>

        </main>

    </div>

    </body>
    </html>
    """

    return html

@app.route("/cambiar-estado", methods=["POST"])
def cambiar_estado():

    compra_id = request.form["compra_id"]
    estado = request.form["estado"]

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute(
        "UPDATE compras SET estado=%s WHERE id=%s",
        (estado, compra_id)
    )

    conexion.commit()

    cursor.close()
    conexion.close()

    return redirect("/admin-usuarios")

@app.route("/eliminar-usuario/<int:id>")
def eliminar_usuario(id):
    if "usuario_correo" not in session:
        return redirect("/login.html")

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("DELETE FROM usuarios WHERE id=%s", (id,))
    conexion.commit()

    cursor.close()
    conexion.close()

    return redirect("/admin-usuarios")


@app.route("/<path:archivo>")
def archivos_estaticos(archivo):
    if os.path.exists(archivo):
        return send_from_directory(".", archivo)

    return "Archivo no encontrado", 404


if __name__ == "__main__":
    app.run(debug=True)