package com.boro.apps.usersrvc.controllers;


import org.springframework.core.io.ClassPathResource;
import org.springframework.core.io.Resource;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class SignUpController {
    @GetMapping(value = "/signup", consumes = MediaType.ALL_VALUE)
    public String signup() {return "signup";}

    @GetMapping(value = {"/static/public/css/style.css", "/users/static/public/css/style.css", "/GatewayApp/src/main/resources/static/public/css/style.css"}
            , produces = "text/css")
    public ResponseEntity<Resource> cssStyle() {
        Resource resource = new ClassPathResource("static/public/css/style.css");

        return ResponseEntity.ok()
                .header("Content-Disposition", "inline")
                .body(resource);
    }
}
