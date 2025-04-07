import psycopg2
from dotenv import load_dotenv
import os
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from weasyprint import HTML
from jinja2 import Template
from io import BytesIO


load_dotenv()

DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASS")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")


def init_engine():
    try:
        conn = psycopg2.connect(
            dbname = DB_NAME,
            user = DB_USER,
            password = DB_PASS,
            host = DB_HOST,
            port = DB_PORT
        )
        
        return conn
    
    except Exception as e:
        st.error(f"Error connecting to the database: {e}")
    
        return None
    

def init_engine_sqlalchemy():
    try:
        db_conn = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
        
        return db_conn
    
    except Exception as e:
        st.error(f"Error connecting to the database using SQLAlchemy: {e}")
    

def insert_data(table_name: str, **data):
    conn = init_engine()
    
    if conn:
        try:
            cur = conn.cursor()
            
            columns = ", ".join(data.keys())
            values_placeholders = ", ".join(["%s"] * len(data))
            
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({values_placeholders})"
            values = tuple(data.values())
            
            cur.execute(query, values)
            conn.commit()
            cur.close()
            
            st.success("Invoice data submitted successfully!")
                    
        except Exception as e:
            st.error(f"Error inserting data: {e}")
            
        finally:
            conn.close()


def get_user_options():
    conn = init_engine()
    
    if conn:
        try:
            cur = conn.cursor()
            query = "SELECT nama FROM invoice_table WHERE is_paid IS NOT TRUE"
            cur.execute(query)
            
            users = [row[0] for row in cur.fetchall()]
            cur.close()
            conn.close()
            
            return users
        
        except Exception as e:
            st.error(f"Error when fetching users: {e}")
            conn.close()
            
            return []
        
    return []


def update_payment_status(name: str):
    conn = init_engine()
    
    if conn:
        try:
            cur = conn.cursor()
            query = "UPDATE invoice_table SET is_paid = TRUE WHERE nama = %s"
            cur.execute(query, (name,))
            conn.commit()
            cur.close()
            conn.close()
            
            return True
        
        except Exception as e:
            st.error(f"Error updating payment status: {e}")
            conn.close()
            
            return False


def fetch_invoice_data():
    conn = init_engine()
    
    if conn:
        try:
            query = "SELECT * FROM invoice_table"
            df = pd.read_sql(sql = query, con = conn)
            conn.close()
            
            return df.sort_values(by = "id_invoice")
        
        except Exception as e:
            st.error(f"Error fetching invoice data from the database: {e}")
            conn.close()
            
            return None
        
    return None


def get_users():
    conn = init_engine()
    
    if conn:
        try:
            cur = conn.cursor()
            query = "SELECT nama FROM invoice_table"
            cur.execute(query)
            
            users = [row[0] for row in cur.fetchall()]
            cur.close()
            conn.close()
            
            return users
        
        except Exception as e:
            st.error(f"Error when fetching users: {e}")
            conn.close()
            
            return []
        
    return []


def get_users_shipping():
    conn = init_engine()
    
    if conn:
        try:
            cur = conn.cursor()
            query = "SELECT nama FROM invoice_table WHERE is_pick_cf is not true"
            cur.execute(query)
            
            users = [row[0] for row in cur.fetchall()]
            cur.close()
            conn.close()
            
            return users
        
        except Exception as e:
            st.error(f"Error when fetching users: {e}")
            conn.close()
            
            return []
        
    return []


def get_qty_data(data: str):
    conn = init_engine()
    
    if not conn:
        return 0  # Return 0 if the connection is not established

    try:
        cur = conn.cursor()

        # Define the query based on the `data` input
        queries = {
            "total": "SELECT SUM(qty) FROM invoice_table",
            "pira": "SELECT SUM(qty) FROM invoice_table WHERE apparel_package = 'Juliana Shafira Package'"
        }
        
        query = queries.get(data)
        if not query:
            return 0  # Return 0 for invalid input data
        
        cur.execute(query)
        result = cur.fetchone()
        
        # Convert result to an integer or return 0 if result is None
        qty_data = int(result[0]) if result and result[0] is not None else 0

        return qty_data
    except Exception as e:
        st.error(f"Error when fetching qty data: {e}")
        return 0  # Return 0 in case of an error
    finally:
        if conn:
            conn.close()  # Ensure the connection is always closed
            

def get_revenue_data(data: str):
    conn = init_engine()
    
    if not conn:
        return 0  # Return 0 if the connection is not established

    try:
        cur = conn.cursor()

        # Define the query based on the `data` input
        queries = {
            "total": "SELECT SUM(total_price) FROM invoice_table",
            "pira": "SELECT SUM(total_price) FROM invoice_table WHERE apparel_package = 'Juliana Shafira Package'"
        }
        
        query = queries.get(data)
        if not query:
            return 0  # Return 0 for invalid input data
        
        cur.execute(query)
        result = cur.fetchone()
        
        # Convert result to an integer or return 0 if result is None
        qty_data = int(result[0]) if result and result[0] is not None else 0

        return qty_data
    except Exception as e:
        st.error(f"Error when fetching qty data: {e}")
        return 0  # Return 0 in case of an error
    finally:
        if conn:
            conn.close()  # Ensure the connection is always closed
            

def get_paid_user_data(data: str):
    conn = init_engine()
    
    if not conn:
        return 0  # Return 0 if the connection is not established

    try:
        cur = conn.cursor()

        # Define the query based on the `data` input
        queries = {
            "paid": "SELECT count(*) FROM invoice_table where is_paid is true",
            "not_paid": "SELECT count(*) FROM invoice_table WHERE is_paid is not true",
        }
        
        query = queries.get(data)
        if not query:
            return 0  # Return 0 for invalid input data
        
        cur.execute(query)
        result = cur.fetchone()
        
        # Convert result to an integer or return 0 if result is None
        qty_data = int(result[0]) if result and result[0] is not None else 0

        return qty_data
    except Exception as e:
        st.error(f"Error when fetching qty data: {e}")
        return 0  # Return 0 in case of an error
    finally:
        if conn:
            conn.close()  # Ensure the connection is always closed


def generate_json_invoice(nama: str):
    data = fetch_invoice_data()
    tmp_data = data.loc[data["nama"] == nama]
    tmp_data = tmp_data.iloc[0]
    
    # get absolute path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))  # Move two levels up to project root
    logo_path = os.path.join(project_root, "assets", "logo_doruken_pira.png")
    absolute_logo_path = f"file://{logo_path}"  # Correct absolute path

    invoice_data = {
        "title": "Doruken x Juliana Shafira Invoice",
        "invoiceNumber": tmp_data["id_invoice"],  # Keep as number
        "issueDate": tmp_data["created_at"].date().strftime('%Y-%m-%d'),
        "dueDate": tmp_data["due_date"].strftime('%Y-%m-%d'),
        "status": bool(tmp_data["is_paid"]),  # Keep as boolean
        "client": {
            "firstName": tmp_data["nama"],
            "lastName": "",
            "phoneNumber": tmp_data["phone"],
            "address": {
                "city": tmp_data["address"],
                "country": "",
            },
            "discordUsername": "",
        },
        "server": {
            "logo": absolute_logo_path,
            "companyName": "Doruken Apparel",
            "firstName": "Doruken",
            "lastName": "",
            "address": {
                "city": "Depok",
                "country": "",
            },
            "discordUsername": "shandytp",
        },
        "itemList": [
            {
                "item": tmp_data["apparel_package"],
                "notes": tmp_data["apparel_size"],
                "qty": tmp_data["qty"],  # Keep as number
                "total": tmp_data["total_price"] - tmp_data["shipping_cost"] - tmp_data["upsize_price"],  # Keep as number
            },
            {
                "item": "Upsize",
                "notes": tmp_data["apparel_size"],
                "qty": tmp_data["qty"],
                "total": tmp_data["upsize_price"] * tmp_data["qty"]
            },
            {
                "item": "Shipping Cost (JNE CTC / REG)",
                "notes": "",
                "qty": "",
                "total": tmp_data["shipping_cost"]
            }
        ],
        "terms": [
            "Untuk pembayaran merch bisa menggunakan Bank BCA / Gopay / Dana / ShopeePay",
            "Jika ada pertanyaan lebih lanjut, bisa langsung tanyakan Contact Person di atas atau menghubungi sosmed Doruken @doruken_"],
    }

    return invoice_data


def generate_shipping_invoice_data(nama: str):
    data = fetch_invoice_data()
    tmp_data = data.loc[data["nama"] == nama].iloc[0]
    
    # Get absolute path for logo
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))  # Move two levels up to project root
    logo_path = os.path.join(project_root, "assets", "logo_doruken_pira.png")
    absolute_logo_path = f"file://{logo_path}"

    shipping_data = {
        "invoiceNumber": tmp_data["id_invoice"],
        "client": {
            "firstName": tmp_data["nama"],
            "lastName": "",
            "phoneNumber": tmp_data["phone"],
            "address": {
                "city": tmp_data["address"]
            }
        },
        "server": {
            "firstName": "Doruken",
            "lastName": "Apparel",
            "phoneNumber": "081235240506",
            "address": {
                "city": "Jl. Lap. Koni I No.27 002Pancoran, RW.2, Pancoran MAS, Kec. Pancoran Mas, Kota Depok, Jawa Barat 16436"
            },
            "logo": absolute_logo_path
        }
    }

    return shipping_data


def render_template_to_pdf(template_file: str, context: dict, styles: list) -> BytesIO:
    """
    Render a Jinja template to a PDF using WeasyPrint and return it as a BytesIO object.
    """
    # Load and render the Jinja template with the provided context
    template = Template(template_file)
    rendered_html = template.render(context)
    
    # DEBUG: Save rendered HTML to a file for inspection
    # with open("debug_rendered_invoice.html", "w") as debug_file:
    #     debug_file.write(rendered_html)

    # Create an in-memory bytes buffer for the PDF
    pdf_buffer = BytesIO()
    HTML(string=rendered_html).write_pdf(pdf_buffer, stylesheets=styles)

    # Reset the buffer's cursor to the start
    pdf_buffer.seek(0)

    return pdf_buffer


def format_currency(value: int) -> str:
    if value == 0:
        return "Rp 0"
    return f"Rp {value:,.0f}".replace(",", ".")
