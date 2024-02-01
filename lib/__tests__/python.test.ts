import * as helper from "../index";

type FunctionMatch = {
  def: string;
  function_indentation: number;
  function_body: string;
  function_parameters: string;
};

type BlockMatch = {
  block_indentation: number;
  block_body: string;
  block_condition: string;
};

describe("python", () => {
  const { python } = helper;
  describe("getDef", () => {
    it("finds function, body, indentation and params", () => {
      const code = `
a = 1

def b(d, e):
  a = 2

def c():
  a = 1
`;
      const match = python.getDef(code, "b");
      expect(match).not.toBeNull();

      const { def, function_indentation, function_body, function_parameters } =
        match as FunctionMatch;
      expect(def).toEqual(`def b(d, e):
  a = 2
`);
      expect(function_indentation).toEqual(0);
      expect(function_body).toEqual("  a = 2\n");
      expect(function_parameters).toEqual("d, e");
    });

    it("handles indentation", () => {
      const code = `
    a = 1
      
    def b(d, e):
      a = 2
    `;
      const match = python.getDef(code, "b");
      expect(match).not.toBeNull();

      const { def, function_indentation, function_body, function_parameters } =
        match as FunctionMatch;
      expect(def).toEqual(`    def b(d, e):
      a = 2
    `);
      expect(function_indentation).toEqual(4);
      expect(function_body).toEqual(`      a = 2\n    `);
      expect(function_parameters).toEqual("d, e");
    });
  });

  describe("removeComments", () => {
    it("removes comments without removing whitespace", () => {
      const code = `
a = 1
# comment
def b(d, e):
  a = 2
  # comment
  return a #comment
`;
      const result = python.removeComments(code);
      expect(result).toEqual(`
a = 1

def b(d, e):
  a = 2
  
  return a 
`);
    });
  });

  describe("getBlock", () => {
    it("finds the body of an if statement", () => {
      const code = `
a = 1

if a == 1:
  a = 2
  b = 3
  if b == 3:
    a = 4

for i in range(10):
  a = 1
`;
      const matches = [
        python.getBlock(code, "if a == 1"),
        python.getBlock(code, /if +\w+ *== *\d+/),
        // eslint-disable-next-line prefer-regex-literals
        python.getBlock(code, new RegExp("if +\\w+ *== *\\d+")),
      ];
      for (const match of matches) {
        expect(match).not.toBeNull();
        // eslint-disable-next-line camelcase
        const { block_indentation, block_body, block_condition } =
          match as BlockMatch;
        expect(block_condition).toEqual("if a == 1");
        expect(block_indentation).toEqual(0);
        expect(block_body).toEqual(
          `  a = 2
  b = 3
  if b == 3:
    a = 4
`
        );
      }

      const matches2 = [
        python.getBlock(code, "for i in range(10)"),
        python.getBlock(code, /for +\w+ +in +range\(\d+\)/),
        // eslint-disable-next-line prefer-regex-literals
        python.getBlock(code, new RegExp("for +\\w+ +in +range\\(\\d+\\)")),
      ];
      for (const match of matches2) {
        expect(match).not.toBeNull();

        // eslint-disable-next-line camelcase
        const { block_indentation, block_body, block_condition } =
          match as BlockMatch;
        expect(block_condition).toEqual("for i in range(10)");
        expect(block_indentation).toEqual(0);
        expect(block_body).toEqual(`  a = 1
`);
      }
    });
  });
});
