using MatrixDepot

# List all problems (Filter some)
list = mdlist("*/*")

# Get matrix A and vector b for all problems
problems = []
prob_count = 0
md_info = 0
for problem in list
    global md_kind = mdinfo(problem).content[4].items[end][1].content[1]  # Nasty

    # Check if type is correct
    if split(md_kind)[1] == "kind:"  # Got the right kind
        kind = join(split(md_kind)[2:end], " ")
        if kind == "least squares problem"
            global prob_count += 1
            print("Found least squares problem n = $(prob_count)\n")
            md = mdopen(problem)
            MatrixDepot.addmetadata!(md.data)
            print("Name = $(md.data.name)\n")
            A = md.A
            new_problem =  Dict("A" => A, "name" => md.data.name)
            try
                new_problem["b"] = md.b                
                print("Storing also b\n")
            catch e
                print("No field b. Creating random one.\n")
                # From python
                # s0 = np.random.randn(m)
                # s0 = np.maximum(s0, 0)
                # x0 = np.random.randn(n)
                # A = np.random.randn(m, n)
                # b = A@x0 + s0
            end
            
            push!(problems, new_problem)
        end
    else
        print("Wrong type extracted from metadata. Type = $(md_kind)\n")
    end
    
end

print("Total number of problems = $(prob_count)\n")
# If vector b does not appear, generate it
