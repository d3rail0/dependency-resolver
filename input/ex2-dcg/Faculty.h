#pragma once

#include <string>
#include <vector>
#include "Student.h"
#include "Professor.h"
#include "Subject.h"


class Faculty {
private:
	std::string _name;
	std::vector<Student> _students;
	std::vector<Professor> _professors;
public:

	Faculty(const std::string& name): _name{name} {}

	std::string getName() const {
		return this->_name;
	}

	const std::vector<Student>& getStudents() const {
		return this->_students;
	}

	const std::vector<Professor>& getProfessors() const {
		return this->_professors;
	}

	void addStudent(const Student& student) {
		this->_students.push_back(student);
	}

	void addProfessor(const Professor& professor) {
		this->_professors.push_back(professor);
	}

};