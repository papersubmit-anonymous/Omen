package org.example;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;

public class WriteToFile {
    public WriteToFile(String logPath, String content){
        try {
            // 获取文件路径
            Path path = Paths.get(logPath);
            // 将内容写入文件
            String contentWithNewLine = content + System.lineSeparator();
            Files.write(path, content.getBytes(StandardCharsets.UTF_8), StandardOpenOption.APPEND);
            //System.out.println(contentWithNewLine);
        } catch (IOException e) {
            System.err.println("Error writing to the file: " + e.getMessage());
        }
    }
}
