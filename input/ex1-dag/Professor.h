#pragma once
#include "Subject.h"
#include "Person.h"

#include <iostream>
#include <vector>

class Professor : public Person {
private:
	std::vector<Subject> _teachingSubjects;
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
