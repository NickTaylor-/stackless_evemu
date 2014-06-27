import io, shutil

matchBytes = bytearray.fromhex("2D FF FF FF 8B 4E 1C 8B  46 20 8B 55 1C 6A 00 6A 00 52 2B C1 50 8B 45 EC  51 50 B3 01 FF 15 18 41 2F 10 8B 4D EC 51 8B F8  FF 15 F4 40 2F 10 85 FF 0F 85")
alreadyPatched = bytearray.fromhex("2D FF FF FF 8B 4E 1C 8B  46 20 8B 55 1C 6A 00 6A 00 52 2B C1 50 8B 45 EC  51 50 B3 01 FF 15 18 41 2F 10 8B 4D EC 51 8B F8  FF 15 F4 40 2F 10 85 FF 90 E9")
patchBytes = bytearray.fromhex("90 E9")

try:
	blueDLLfile = open("blue.dll", "r+b", buffering=0)
	blueDLL = blueDLLfile.readall()

	# Find pattern
	print("Searching for match")
	matchedBytes = 0
	offset = -1
	for byte in blueDLL:
		if matchedBytes == 49:
			break

		if byte == matchBytes[matchedBytes]:
			matchedBytes += 1
		else:
			matchedBytes = 0

		offset += 1

	if matchedBytes != 49:
		for byte in blueDLL:
			if matchedBytes == 49:
				break

			if byte == alreadyPatched[matchedBytes]:
				matchedBytes += 1
			else:
				matchedBytes = 0

		if matchedBytes == 49:
			print("Blue.dll is already patched, exiting.")
		else:
			print("No match found.")
	else:
		print("Match found at offset ", '0x{0:08X}'.format(offset))

		# Backup file
		print("Backing up blue.dll to blue.dll.bak")
		shutil.copyfile("blue.dll", "blue.dll.bak")

		# Patch DLL
		print("Writing patch to blue.dll")
		blueDLLfile.seek(offset)
		blueDLLfile.write(patchBytes)

		print("Sucessfully patched, enjoy!")

except OSError as e:
	print(e.strerror)