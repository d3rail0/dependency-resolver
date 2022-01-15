#pragma once

#include <string>

class Person {
private:
	std::string _name;
	int _age;
protected:
	Person(const std::string& name, int age): _name{name}, _age{age} {}
public:

	Person() = delete;

	virtual ~Person() {}

	std::string getName() const {
		return this->_name;
	}

	int getAge() const {
		return this->_age;
	}

};