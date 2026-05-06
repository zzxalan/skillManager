package com.outbook.smart.__JAVA_PACKAGE_FRAGMENT__;

import com.outbook.plugin.bootstrap.SpringPluginBootstrap;
import com.outbook.plugin.bootstrap.coexist.CoexistAllowAutoConfiguration;
import com.outbook.smart.Application;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class PluginApplication extends SpringPluginBootstrap {

    public static void main(String[] args) {
        new PluginApplication().run(Application.class, args);
    }

    @Override
    protected void configCoexistAllowAutoConfiguration(CoexistAllowAutoConfiguration config) {
        config.add("com.mybatisflex.spring.boot.MybatisFlexAutoConfiguration");
        config.add("org.springframework.boot.autoconfigure.flyway.FlywayAutoConfiguration");
        config.add("org.springframework.boot.autoconfigure.jdbc.DataSourceTransactionManagerAutoConfiguration");
    }
}
