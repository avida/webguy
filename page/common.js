var _r=function(p,c){return p.replace(/%s/,c);}

function format(template, args)
{
    return [].concat(args).reduce(_r, template)
}
