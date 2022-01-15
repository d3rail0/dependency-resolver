#pragma once
#include "Person.h"
#include <iostream>

class Student : public Person {
private:
	int _studyLevel;
public:

	Student(const std::string& name, int age, int studyLevel): 
		Person(name,age), _studyLevel{ studyLevel } {}

	int getStudyLevel() const {
		return this->_studyLevel;
	}

	friend std::ostream& operator<<(std::ostream& os, const Student& student);

};

std::ostream& operator<<(std::ostream&, const Student&);