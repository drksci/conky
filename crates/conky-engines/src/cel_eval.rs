use cel_interpreter::{Context, Program, Value};
use std::collections::HashMap;

pub struct CelEvaluator {}

impl CelEvaluator {
    pub fn new() -> Self {
        Self {}
    }

    /// Evaluates a CEL boolean expression given string/number context variables
    pub fn eval_bool(expr: &str, vars: &HashMap<String, f64>) -> Result<bool, anyhow::Error> {
        let program = Program::compile(expr)
            .map_err(|e| anyhow::anyhow!("Failed to compile CEL expression '{}': {:?}", expr, e))?;

        let mut ctx = Context::default();
        for (k, v) in vars {
            ctx.add_variable(k.as_str(), Value::from(*v))
                .map_err(|e| anyhow::anyhow!("Failed binding variable {}: {:?}", k, e))?;
        }

        let val = program
            .execute(&ctx)
            .map_err(|e| anyhow::anyhow!("Failed evaluating CEL '{}': {:?}", expr, e))?;

        match val {
            Value::Bool(b) => Ok(b),
            _ => anyhow::bail!("CEL expression did not return a boolean: {:?}", val),
        }
    }
}

impl Default for CelEvaluator {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_cel_watch_evaluation() {
        let mut vars = HashMap::new();
        vars.insert("order_qty".into(), 4.0);
        vars.insert("heat".into(), 0.85);

        assert!(CelEvaluator::eval_bool("order_qty > 0.0", &vars).unwrap());
        assert!(CelEvaluator::eval_bool("heat > 0.8", &vars).unwrap());
        assert!(!CelEvaluator::eval_bool("heat > 0.9", &vars).unwrap());
    }
}
