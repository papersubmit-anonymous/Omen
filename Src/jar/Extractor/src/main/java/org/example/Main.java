package org.example;

import com.github.javaparser.JavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.Modifier;
import com.github.javaparser.ast.body.ClassOrInterfaceDeclaration;
import com.github.javaparser.ast.body.InitializerDeclaration;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.body.Parameter;
import com.github.javaparser.ast.expr.MethodCallExpr;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;
import org.example.WriteToFile;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Stream;


public class Main {
    public static String LogPath = "D:\\PythonProject\\DeedPool\\test\\";
    public static void main(String[] args) {

        if (args.length != 2) {
            System.out.println("Usage: java Main <path_to_java_files_directory> <path_to_log_files>");
            System.exit(1);
        }

        String dirPath = args[0];
        LogPath = args[1];
        //String dirPath = "D:\\PythonProject\\DeedPool\\workDirs\\com_example_myapplication\\sources";
        //String dirPath = "D:\\PythonProject\\DeedPool\\workDirs\\com_v2ray_ang\\sources";
        //String dirPath = "D:\\PythonProject\\DeedPool\\test\\";
        //LogPath = "D:\\PythonProject\\DeedPool\\test\\log.txt";
        try {
            FileWriter fileWriter = new FileWriter(LogPath, false); // false表示不追加，而是覆盖文件内容
            fileWriter.close(); // 关闭文件写入器，清空文件内容
        } catch (IOException e) {
            System.err.println("Error while clearing the file: " + e.getMessage());
        }

        // 创建一个空的ArrayList
        ArrayList<String> filterPaths = new ArrayList<String>();

        try (Stream<Path> paths = Files.walk(Paths.get(dirPath))) {
            // 递归遍历目录，返回所有子目录和文件的路径
            paths.filter(Files::isRegularFile) // 过滤掉目录，只保留文件
                    .filter(path -> path.toString().endsWith(".java")) // 过滤掉目录，只保留文件
                    .forEach(path -> filterPaths.add(path.toString())); // 将Java源代码文件添加到JavaProjectBuilder中
        } catch (Exception e) {
            System.err.println("Error while reading Java files: " + e.getMessage());
            //System.exit(1);
        }

        for (String element : filterPaths) {
            //System.out.println(element);
            try {
                File javaFile = new File(element);
                CompilationUnit compilationUnit = JavaParser.parse(javaFile);
                String packageName = "";
                if (compilationUnit.getPackageDeclaration().isPresent()){
                    packageName = String.valueOf(compilationUnit.getPackageDeclaration().get());
                }
                System.out.println("packageName: " + packageName);
                new WriteToFile(Main.LogPath, "@@@@@@@@@@@@[+]New Package@@@@@@@@@@@@\n");
                new WriteToFile(Main.LogPath, "Package Name: " + packageName + "\n");
                //System.out.println(compilationUnit);
                ClassVisitor classVisitor = new ClassVisitor();

                classVisitor.visit(compilationUnit, null);
                new WriteToFile(Main.LogPath, "@@@@@@@@@@@@@@@@@@@@@@@@\n");

            } catch (IOException e) {
                System.err.println("Error reading the Java file: " + e.getMessage());
            } catch (Exception e) {
                System.err.println("Error processing the Java file: " + e.getMessage() + ". Skipping this file.");
            }
        }

    }

    private static class ClassVisitor extends VoidVisitorAdapter<Void> {
        @Override
        public void visit(ClassOrInterfaceDeclaration classOrInterfaceDeclaration, Void arg) {
            super.visit(classOrInterfaceDeclaration, arg);
            // 获取类名称
            String className = classOrInterfaceDeclaration.getNameAsString();
            System.out.println("Class Name: " + className);
            new WriteToFile(Main.LogPath, "=====[+]New Class=====\n");
            new WriteToFile(Main.LogPath, "Class Name: " + className + "\n");
            MethodVisitor methodVisitor = new MethodVisitor();
            methodVisitor.visit(classOrInterfaceDeclaration, arg);

            InitializerVisitor initializerVisitor = new InitializerVisitor();
            initializerVisitor.visit(classOrInterfaceDeclaration, arg);
            new WriteToFile(Main.LogPath, "===============\n");
        }
    }
    private static class MethodVisitor extends VoidVisitorAdapter<Void> {
        @Override
        public void visit(MethodDeclaration methodDeclaration, Void arg) {
            super.visit(methodDeclaration, arg);
            // 添加调试输出
            System.out.println("Visiting method: " + methodDeclaration.getSignature());
            if (methodDeclaration.getModifiers().contains(Modifier.NATIVE)) {
                System.out.println("Found native method: " + methodDeclaration.getSignature());
                boolean isStatic = methodDeclaration.getModifiers().contains(Modifier.STATIC);
                // 获取返回值类型
                String returnType = methodDeclaration.getType().asString();
                System.out.println("Return type: " + returnType);
                // 获取参数列表
                List<Parameter> parameters = methodDeclaration.getParameters();
                // 获取参数个数
                int parameterCount = parameters.size();
                System.out.println("Parameter count: " + parameterCount);
                new WriteToFile(Main.LogPath, "$$$$$[+]New Method$$$$$\n");
                new WriteToFile(Main.LogPath, "Found native method: " + methodDeclaration.getSignature() + "\n");
                if(isStatic){
                    System.out.println("Is static: Static");
                    new WriteToFile(Main.LogPath, "Is static: Static\n");
                }else {
                    System.out.println("Is static: Dymaic");
                    new WriteToFile(Main.LogPath, "Is static: Dymaic\n");
                }
                new WriteToFile(Main.LogPath, "Return type: " + returnType + "\n");
                new WriteToFile(Main.LogPath, "Parameter count: " + parameterCount + "\n");
                // 输出每个参数的类型和名称
                for (Parameter parameter : parameters) {
                    System.out.println("Parameter type: " + parameter.getType() + ", Parameter name: " + parameter.getName());
                    new WriteToFile(Main.LogPath, "Parameter type: " + parameter.getType() + ", Parameter name: " + parameter.getName() + "\n");
                }
                new WriteToFile(Main.LogPath, "$$$$$$$$$$$$$$$$" + "\n");
            }
        }
    }
    private static class InitializerVisitor extends VoidVisitorAdapter<Void> {
        @Override
        public void visit(InitializerDeclaration initializerDeclaration, Void arg) {
            super.visit(initializerDeclaration, arg);
            new WriteToFile(Main.LogPath, "****[+] New Library****" + "\n");
            if (initializerDeclaration.isStatic()) {
                initializerDeclaration.findAll(MethodCallExpr.class).stream()
                        .filter(methodCallExpr -> methodCallExpr.getNameAsString().equals("loadLibrary"))
                        .filter(methodCallExpr -> methodCallExpr.getScope().isPresent() &&
                                methodCallExpr.getScope().get().toString().equals("System"))
                        .forEach(methodCallExpr -> new WriteToFile(Main.LogPath, "Found System.loadLibrary call: " + methodCallExpr + "\n"));
            }
            new WriteToFile(Main.LogPath, "********" + "\n");
        }
    }

}
