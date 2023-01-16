from flask import Flask, jsonify, request
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

uri = os.getenv('URI')
user = os.getenv("USERNAME_NEO4J")
password = os.getenv("PASSWORD")
driver = GraphDatabase.driver(uri, auth=(user, password), database="neo4j")


def get_employees(tx):
    query = "MATCH (e:Employee) RETURN e"
    results = tx.run(query).data()
    employees = [{'first_name': result['e']['first_name'], 'last_name': result['e']['last_name'],
                  'position': result['e']['position']} for result in results]
    return employees


@app.route('/employees', methods=['GET'])
def get_employees_route():
    with driver.session() as session:
        employees = session.read_transaction(get_employees)

    response = {'employees': employees}
    return response


def add_employee(tx, first_name, last_name, position):
    query = "CREATE (e:Employee {first_name: $first_name, last_name: $last_name, position: $position})"
    tx.run(query, first_name=first_name, last_name=last_name, position=position)


@app.route('/employees', methods=['POST'])
def add_employee_route():
    first_name = request.json['first_name']
    last_name = request.json['last_name']
    position = request.json['position']

    if not first_name or not last_name or not position:
        response = {"message": "Please check the request data"}
        return jsonify(response)

    with driver.session() as session:
        employees = session.read_transaction(get_employees)

    for i in employees:
        if i['first_name'] == first_name and i['last_name'] == last_name:
            response = {"message": "This person already exists"}
            return jsonify(response)

    with driver.session() as session:
        session.write_transaction(add_employee, first_name, last_name, position)

    response = {'status': 'success'}
    return jsonify(response)


def update_employee(tx, id, first_name, last_name, position):
    query = "MATCH (e:Employee) WHERE id(e)=$id RETURN e"
    result = tx.run(query, id=int(id)).data()
    if not result:
        return None
    query = "MATCH (e:Employee) WHERE id(e)=$id SET e.first_name=$first_name, e.last_name=$last_name, e.position=$position"
    tx.run(query, id=int(id), first_name=first_name, last_name=last_name, position=position)
    return "Done"


@app.route("/employees/<string:id>", methods=['PUT'])
def update_employee_route(id):
    first_name = request.json['first_name']
    last_name = request.json['last_name']
    position = request.json['position']

    with driver.session() as session:
        employee = session.write_transaction(update_employee, id, first_name, last_name, position)

    if not employee:
        response = {'message': 'Employee not found'}
        return jsonify(response), 404

    response = {'status': 'success'}
    return jsonify(response)


def delete_employee(tx, id):
    query = "MATCH (e:Employee) WHERE id(e)=$id DETACH DELETE e"
    result = tx.run(query, id=int(id))
    if not result:
        return None
    return "Deleted"


@app.route("/employees/<string:id>", methods=['DELETE'])
def delete_employee_route(id):
    with driver.session() as session:
        res = session.write_transaction(delete_employee, id)

    if not res:
        response = {'message': 'Employee not found'}
        return jsonify(response), 404

    response = {'status': 'success'}
    return jsonify(response)


def find_employee_subordinates(tx, id):
    query = "MATCH (e:Employee) WHERE id(e)=$id RETURN e"
    result = tx.run(query, id=int(id)).data()
    if not result:
        return None
    query = "MATCH (e:Employe)-[:MANAGES]->(sub:Employee) WHERE id(e)=$id RETURN sub"
    results = tx.run(query, id=int(id)).data()
    subordinates = [{'first_name': result['e']['first_name'], 'last_name': result['e']['last_name'],
                     'position': result['e']['position']} for result in results]
    return subordinates


@app.route("/employees/:id/subordinates", methods=["GET"])
def find_employee_subordinates_route(id):
    with driver.session() as session:
        employees = session.read_transaction(find_employee_subordinates, id)

    response = {f'subordinates of {id}': employees}

    return response


def find_department_by_employee(tx, id):
    query = "MATCH (e:Employee)-[:WORKS_IN]->(d:Department) WHERE id(e)=$id RETURN d"
    results = tx.run(query, id=int(id)).data()
    if not results:
        return None
    department_data = [{'name': result['d']['name'], "Reszta danych": '...'} for result in results]
    return department_data


@app.route("/employees/:id/department", methods=['GET'])
def find_department_by_employee_route(id):
    with driver.session() as session:
        departament = session.read_transaction(find_department_by_employee, id)

    response = {f'departament of {id}': departament}

    return response


def get_departments(tx):
    query = "MATCH (d:Department) RETURN d"
    results = tx.run(query).data()
    department_data = [{'name': result['d']['name'], "Reszta danych": '...'} for result in results]
    return department_data


@app.route("/departments", methods=['GET'])
def get_departments_route():
    with driver.session() as session:
        departments = session.read_transaction(get_departments)

    response = {"departments": departments}
    return response


def find_employees_of_department(tx, id):
    query = "MATCH (e:Employee)-[:WORKS_IN]->(d:Department) WHERE id(d)=$id RETURN e"
    results = tx.run(query, id=int(id)).data()
    if not results:
        return None
    employees = [{'first_name': result['e']['first_name'], 'last_name': result['e']['last_name'],
                  'position': result['e']['position']} for result in results]
    return employees


@app.route("/departments/:id/employees", methods=['GET'])
def get_departments_route(id):
    with driver.session() as session:
        employees = session.read_transaction(find_employees_of_department, id)

    response = {"employees": employees}
    return response


if __name__ == '__main__':
    app.run()
