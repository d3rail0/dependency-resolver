#pragma once
#include "Subject.h"
#include "Person.h"

#include <iostream>
#include <vector>

// #include "Faculty.h"

class Professor : public Person {
private:
	std::vector<Subject> _teachingSubjects;

	// Will require including Faculty header file
	// which will cause cyclic dependency because
	// class Professor depends on Faculty & Faculty depends on Professor
	Faculty* _faculty;


public:

	Professor(const std::string& name, int age) :
		Person(name, age), _teachingSubjects{ } {}

	const std::vector<Subject>& getTeachingSubjects() const {
		return this->_teachingSubjects;
	}

	void addTeachingSubject(const std::string& name, int lectureCount, int exCount) {
		Subject subject;
		subject.name = name;
		subject.lectureCount = lectureCount;
		subject.exerciseCount = exCount;
		this->_teachingSubjects.push_back(subject);
	}


	friend std::ostream& operator<<(std::ostream&, const Professor&);

};

std::ostream& operator<<(std::ostream&, const Professor&);
