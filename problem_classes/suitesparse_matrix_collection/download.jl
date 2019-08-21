using MatrixDepot
using SparseArrays
using MAT
using Random
rand(0)

accepted_problems = ["least squares problem", "optimization problem"]

# List all problems (Filter some)
list = mdlist("*/*")

# Get matrix A and vector b for all problems
prob_count = 0
md_info = 0
for problem in list
    global md_kind = mdinfo(problem).content[4].items[end][1].content[1]  # Nasty

    # Check if type is correct
    if split(md_kind)[1] == "kind:"  # Got the right kind
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
                # print("Type of A ", typeof(new_problem["A"]), "\n")
                # print("Type of b ", typeof(new_problem["b"]), "\n")
                # print("Type of name ", typeof(new_problem["name"]), "\n")
                matwrite(file_name, new_problem)
            catch e
                print(e)
                break
            end
            
            print("Written to file $(file_name)\n")
        end
    else
        print("Wrong type extracted from metadata. Type = $(md_kind)\n")
    end
    
end

print("Total number of problems = $(prob_count)\n")
