using MatrixDepot
using SparseArrays
using MAT
using Random
rand(0)

accepted_problems = ["least squares problem"]

# List all problems (Filter some)
list = mdlist("*/*")

# Get matrix A and vector b for all problems
prob_count = 0
md_info = 0
for problem in list
    # Try to extract the kind field from metadata more robustly
    info = mdinfo(problem)
    md_kind = nothing

    # Search through content items to find the "kind:" field
    try
        for content_item in info.content
            if hasfield(typeof(content_item), :items)
                for item in content_item.items
                    if length(item) > 0 && hasfield(typeof(item[1]), :content)
                        for text in item[1].content
                            # Convert to string to handle Markdown formatting objects
                            text_str = string(text)
                            if occursin("kind:", text_str)
                                md_kind = text_str
                                break
                            end
                        end
                    end
                    if !isnothing(md_kind)
                        break
                    end
                end
            end
            if !isnothing(md_kind)
                break
            end
        end
    catch e
        println("Could not extract metadata for problem $(problem): $(e)")
        continue
    end

    # Check if we found the kind field and if type is correct
    if !isnothing(md_kind) && split(md_kind)[1] == "kind:"  # Got the right kind
        kind = join(split(md_kind)[2:end], " ")
        if kind in accepted_problems
            md = mdopen(problem)
            MatrixDepot.addmetadata!(md.data)
            print("Name = $(md.data.name)\n")
            A = float(md.A)
            if issymmetric(A)
                print("Making it a generic matrix\n")
                A = SparseMatrixCSC(A)
            end
            global prob_count += 1
            print("Found $(kind) n = $(prob_count)\n")
            (m, n) = size(A)
            new_problem =  Dict("A" => A, "name" => md.data.name)
            try
                new_problem["b"] = float(md.b)
                print("Storing also b\n")
            catch e
                print("No field b. Creating random one.\n")
                s0 = randn(m)
                x0 = randn(n)
                b = A * x0 + s0
                new_problem["b"] = b
            end
            file_name = replace("$(md.data.name).mat", "/" => "_")
            try
                matwrite(file_name, new_problem)
            catch e
                print(e)
                break
            end
            
            print("Written to file $(file_name)\n")
        end
    elseif !isnothing(md_kind)
        print("Wrong type extracted from metadata. Type = $(md_kind)\n")
    end
    
end

print("Total number of problems = $(prob_count)\n")
