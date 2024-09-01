package com.boro.apps;

import com.ulisesbocchio.jasyptspringboot.annotation.EnableEncryptableProperties;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.servlet.config.annotation.EnableWebMvc;

@SpringBootApplication
@EnableEncryptableProperties
@EnableWebMvc
public class MonitoringExpertiseApplication
{
    public static void main( String[] args )
    {
        SpringApplication.run(MonitoringExpertiseApplication.class, args);
    }
}
