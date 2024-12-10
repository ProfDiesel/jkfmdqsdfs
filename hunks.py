def split():
    for line in stream.splitline():
        
    def splitByHunk
        legacy = false
        outfile = nil
        stream = open(@filename, 'rb')
        filename = ""
        counter = 0
        header = []

        until (stream.eof?)
            line = stream.readline.encode("UTF-8", @encode)

            # We need to create a new file
            if (line =~ /^Index: .*/) == 0
                # Patch includes Index lines
                # Drop into "legacy mode"
                legacy = true
                filename = getFilename(line)
                header << line

                # Remaining 3 lines of header
                for i in 0..2
                    line = stream.readline
                    header << line
                end

                counter = 0
            elsif (line =~ /--- .*/) == 0 and not legacy
                #find filename
                # next line is header too
                header = [ line, stream.readline ]
                filename = getFilenameByHeader(header)
                counter = 0
            elsif (line =~ /@@ .* @@/) == 0
                if (outfile)
                    outfile.close_write
                end

                zero = counter.to_s.rjust(3, '0')
                hunkfilename = "#{filename}.#{zero}.patch"
                outfile = createFile(hunkfilename)
                counter += 1

                outfile.write(header.join(''))
                outfile.write(line)
            else
                if outfile
                    outfile.write(line)
                end
            end
        end
    end