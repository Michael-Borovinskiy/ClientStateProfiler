package com.boro.apps.usersrvc.exceptions;

public class UserAlreadyExistException extends Exception{

    public UserAlreadyExistException(String message) {
        System.out.println(message);
    }

    public UserAlreadyExistException(Throwable cause) {

        super(cause);
    }

    public UserAlreadyExistException(String message, Throwable cause) {

        super(message, cause);
    }
}