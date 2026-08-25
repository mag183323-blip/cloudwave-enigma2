ZIP_NAME=cloudwave-enigma2.zip

all:
	zip -r $(ZIP_NAME) CloudWave

clean:
	rm -f $(ZIP_NAME)